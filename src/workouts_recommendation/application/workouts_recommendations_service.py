from pathlib import Path
from typing import List, Tuple

import joblib
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

from src.common.application.localizations import localize as _
from src.common.domain.response import Error, Response, Status
from src.constants import WorkoutsRecommendationErrorCodes
from src.workouts.domain.workouts import Workout
from src.workouts_recommendation.domain.response import (ModelTrainingResponse,
                                                         PredictionResponse,
                                                         TrainingResult)

_MODEL_DIR = Path("models")
_SCALER_DIR = Path("models/scalers")
_MODEL_DIR.mkdir(parents=True, exist_ok=True)
_SCALER_DIR.mkdir(parents=True, exist_ok=True)


def _build_lstm(input_dim: int, lookback: int) -> Sequential:
    model = Sequential([
        LSTM(64, input_shape=(lookback, input_dim)),
        Dense(32, activation="relu"),
        Dense(2)                                   # duration, intensity
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def _prepare_workouts(
        workouts: List[Workout],
        lookback: int = 4,
        batch_size: int = 32,
        test_split: float = 0.2
) -> Tuple[
        TimeseriesGenerator,
        TimeseriesGenerator,
        StandardScaler,
        StandardScaler,
        List[str]
]:
    rows = [{
        "sleep_score": w.sleep_score,
        "duration":    w.duration,
        "intensity":   w.intensity,
        "day_of_week": w.get_day_of_week(),
        "time_of_day": w.get_time_of_day(),
    } for w in workouts]

    df = pd.DataFrame(rows)

    X_df = pd.get_dummies(
        df[["day_of_week", "time_of_day", "sleep_score"]],
        columns=["day_of_week", "time_of_day"]
    ).astype(float)
    feature_cols = X_df.columns.tolist()

    y = df[["duration", "intensity"]].values

    scaler_X = StandardScaler().fit(X_df)
    scaler_y = StandardScaler().fit(y)

    X_scaled = scaler_X.transform(X_df).astype(float)
    y_scaled = scaler_y.transform(y).astype(float)

    split = int(len(X_scaled) * (1 - test_split))
    X_train, X_test = X_scaled[:split], X_scaled[split:]
    y_train, y_test = y_scaled[:split], y_scaled[split:]

    train_gen = TimeseriesGenerator(
        X_train, y_train, length=lookback, batch_size=batch_size
    )
    test_gen = TimeseriesGenerator(
        X_test, y_test, length=lookback, batch_size=batch_size
    )

    return train_gen, test_gen, scaler_X, scaler_y, feature_cols


def train_for_user(
        user_id: str,
        workouts: List[Workout],
        language: str,
        epochs: int = 200,
        lookback: int = 4
) -> tuple[Response, int]:
    """
    Entrena la red neuronal RNN de un usuario y guarda:
       • models/{user_id}.keras
       • models/scalers/{user_id}_X.pkl   (dict {"scaler", "cols"})
       • models/scalers/{user_id}_y.pkl
    Devuelve métricas finales para la API.
    """
    workouts = list(workouts)
    if len(workouts) < lookback + 1:
        error = Error(WorkoutsRecommendationErrorCodes.INSUFFICIENT_WORKOUTS, _(
            WorkoutsRecommendationErrorCodes.INSUFFICIENT_WORKOUTS, language))
        response = ModelTrainingResponse(status=Status.ERROR, error=error)
        return response, 400

    (train_gen, test_gen,
     scaler_X, scaler_y,
     feature_cols) = _prepare_workouts(workouts,
                                       lookback=lookback,
                                       batch_size=32,
                                       test_split=0.2)

    model = _build_lstm(input_dim=train_gen.data.shape[1], lookback=lookback)

    history = model.fit(
        train_gen,
        validation_data=test_gen,
        epochs=epochs,
        verbose=0
    )

    model_path = _MODEL_DIR / f"{user_id}.keras"
    scalerX_path = _SCALER_DIR / f"{user_id}_X.pkl"
    scalerY_path = _SCALER_DIR / f"{user_id}_y.pkl"

    model.save(model_path, overwrite=True)
    joblib.dump({"scaler": scaler_X, "cols": feature_cols}, scalerX_path)
    joblib.dump(scaler_y, scalerY_path)

    training_result = convert_history_to_response(
        model_path=model_path,
        epochs=epochs,
        history=history
    )
    response = ModelTrainingResponse(
        status=Status.SUCCESS,
        result=training_result
    )
    return response, 200


def convert_history_to_response(model_path, epochs, history) -> TrainingResult:
    return TrainingResult(
        model_path=str(model_path),
        epochs=epochs,
        loss=float(history.history["loss"][-1]),
        val_loss=float(history.history["val_loss"][-1]),
        mae=float(history.history["mae"][-1]),
        val_mae=float(history.history["val_mae"][-1]),
    )


def predict_next_for_user(
        user_id: str,
        recent_workouts: List[Workout],
        language: str,
        lookback: int = 4
) -> tuple[Response, int]:
    recent_workouts = list(recent_workouts)
    if len(recent_workouts) < lookback:
        error = Error(WorkoutsRecommendationErrorCodes.INSUFFICIENT_WORKOUTS, _(
            WorkoutsRecommendationErrorCodes.INSUFFICIENT_WORKOUTS, language))
        response = PredictionResponse(status=Status.ERROR, error=error)
        return response, 400

    model_path = _MODEL_DIR / f"{user_id}.keras"
    scalerX_path = _SCALER_DIR / f"{user_id}_X.pkl"
    scalerY_path = _SCALER_DIR / f"{user_id}_y.pkl"

    if not model_path.exists():
        raise FileNotFoundError(f"No model found for user {user_id}")

    model = load_model(model_path)

    meta = joblib.load(scalerX_path)
    if isinstance(meta, dict):
        scaler_X = meta["scaler"]
        feature_cols = meta["cols"]
    else:
        scaler_X = meta
        feature_cols = getattr(scaler_X, "feature_names_in_", None)
        if feature_cols is None:
            raise RuntimeError("Scaler sin lista de columnas")

    scaler_y = joblib.load(scalerY_path)

    rows = [{
        "sleep_score": w.sleep_score,
        "day_of_week": w.get_day_of_week(),
        "time_of_day": w.get_time_of_day(),
    } for w in recent_workouts[-lookback:]]

    X_new = pd.get_dummies(
        pd.DataFrame(rows),
        columns=["day_of_week", "time_of_day"]
    ).astype(float)

    X_new = X_new.reindex(columns=feature_cols, fill_value=0)

    X_scaled = scaler_X.transform(X_new)
    X_scaled = X_scaled.reshape(1, lookback, -1)

    y_pred_scaled = model.predict(X_scaled, verbose=0)
    duration, intensity = scaler_y.inverse_transform(y_pred_scaled)[0]
    scaled_intensity = round(float(intensity) * 4) + 1
    scaled_intensity = max(1, min(5, scaled_intensity))

    return PredictionResponse(
        status=Status.SUCCESS,
        duration=int(duration),
        intensity=scaled_intensity
    ), 200
