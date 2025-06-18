from src.common.domain.response import Error, Response, Status


class PredictionResponse(Response):
    def __init__(self, status: Status, error: Error | None = None, duration: int = -1, intensity: int = -1):
        super().__init__(status=status, error=error)
        self.duration = duration
        self.intensity = intensity

    def to_json(self):
        response = super().to_json()
        if self.error is None:
            response['duration'] = self.duration
            response['intensity'] = self.intensity
        return response


class TrainingResult:
    def __init__(self, model_path: str, epochs: int, loss: float, val_loss: float, mae: float, val_mae: float):
        self.model_path = model_path
        self.epochs = epochs
        self.loss = loss
        self.val_loss = val_loss
        self.mae = mae
        self.val_mae = val_mae

    def to_dict(self) -> dict:
        return {
            "model_path": self.model_path,
            "epochs": self.epochs,
            "loss": self.loss,
            "val_loss": self.val_loss,
            "mae": self.mae,
            "val_mae": self.val_mae,
        }


class ModelTrainingResponse(Response):
    def __init__(self, status: Status, error: Error | None = None, result: TrainingResult | None = None):
        super().__init__(status=status, error=error)
        self.result = result

    def to_json(self):
        json_response = super().to_json()
        if self.result:
            json_response['result'] = self.result.to_dict()
        return json_response
