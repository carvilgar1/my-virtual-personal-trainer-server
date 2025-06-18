import unittest
from unittest.mock import MagicMock, patch

from src.common.domain.response import Status
from src.common.domain.user_credentials import UserCredentials
from src.workouts.controllers import controllers
from src.workouts.domain.workouts import Warning, Workout


class TestWorkoutsControllers(unittest.TestCase):
    def setUp(self):
        self.user = UserCredentials(
            '123', 'test@email.com', 'testuser', 'hash')
        self.language = 'en'
        self.mock_repo = MagicMock()
        self.dummy_workout = MagicMock(spec=Workout)
        self.dummy_warning = MagicMock(spec=Warning)

    @patch('src.workouts.controllers.controllers.process_workout_data')
    def test_save_user_workouts_empty_list(self, mock_process):
        response, status = controllers.save_user_workouts(
            self.user, self.mock_repo, [], self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    @patch('src.workouts.controllers.controllers.process_workout_data')
    def test_save_user_workouts_none(self, mock_process):
        response, status = controllers.save_user_workouts(
            self.user, self.mock_repo, None, self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    @patch('src.workouts.controllers.controllers.process_workout_data')
    def test_save_user_workouts_not_list(self, mock_process):
        response, status = controllers.save_user_workouts(
            self.user, self.mock_repo, "not_a_list", self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    @patch('src.workouts.controllers.controllers.process_workout_data')
    def test_save_user_workouts_all_invalid(self, mock_process):
        def fake_process(lang, workouts, wrong, accepted):
            wrong.append(self.dummy_warning)
        mock_process.side_effect = fake_process

        response, status = controllers.save_user_workouts(
            self.user, self.mock_repo, [{}], self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    @patch('src.workouts.controllers.controllers.process_workout_data')
    def test_save_user_workouts_partial_success(self, mock_process):
        def fake_process(lang, workouts, wrong, accepted):
            accepted.append(self.dummy_workout)
            wrong.append(self.dummy_warning)
        mock_process.side_effect = fake_process

        response, status = controllers.save_user_workouts(
            self.user, self.mock_repo, [{}], self.language
        )
        self.assertEqual(status, 207)
        self.assertEqual(response.status, Status.WARNING)

    @patch('src.workouts.controllers.controllers.process_workout_data')
    def test_save_user_workouts_all_success(self, mock_process):
        def fake_process(lang, workouts, wrong, accepted):
            accepted.append(self.dummy_workout)
        mock_process.side_effect = fake_process

        response, status = controllers.save_user_workouts(
            self.user, self.mock_repo, [{}], self.language
        )
        self.assertEqual(status, 200)
        self.assertEqual(response.status, Status.SUCCESS)

    def test_retrieve_workouts_by_pages(self):
        self.mock_repo.retrieve_workouts.return_value = [self.dummy_workout]
        response, status = controllers.retrieve_workouts_by_pages(
            self.user, self.mock_repo, 1, 100
        )
        self.assertEqual(status, 200)
        self.assertEqual(response.status, Status.SUCCESS)
        self.mock_repo.retrieve_workouts.assert_called_once_with(
            self.user.user_id, 1, 100
        )

    def test_retrieve_workouts_by_pages_invalid_page(self):
        self.mock_repo.retrieve_workouts.return_value = [self.dummy_workout]
        _, status = controllers.retrieve_workouts_by_pages(
            self.user, self.mock_repo, -5, 2000
        )
        self.assertEqual(status, 200)
        self.mock_repo.retrieve_workouts.assert_called_once_with(
            self.user.user_id, 1, 1000
        )

    def test_retrieve_workouts_by_dates_success(self):
        response, status = controllers.retrieve_workouts_by_dates(
            self.user, self.mock_repo, '2024-01-01', '2024-01-10', self.language
        )
        self.assertEqual(status, 200)
        self.assertEqual(response.status, Status.SUCCESS)

    def test_retrieve_workouts_by_dates_invalid_date_from(self):
        response, status = controllers.retrieve_workouts_by_dates(
            self.user, self.mock_repo, 'bad', '2024-01-10', self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    def test_retrieve_workouts_by_dates_invalid_date_to(self):
        response, status = controllers.retrieve_workouts_by_dates(
            self.user, self.mock_repo, '2024-01-10',  'bad',  self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    def test_retrieve_workouts_by_dates_range_exceeded(self):
        response, status = controllers.retrieve_workouts_by_dates(
            self.user, self.mock_repo, '2020-01-01', '2024-01-10', self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    @patch('src.workouts.controllers.controllers.validate_date')
    def test_retrieve_workouts_by_dates_date_to_before_date_from(self, mock_validate_date):
        date_from = MagicMock()
        date_to = MagicMock()
        date_from.__gt__.return_value = True  # date_from > date_to
        mock_validate_date.side_effect = [
            (date_from, None),
            (date_to, None)
        ]
        response, status = controllers.retrieve_workouts_by_dates(
            self.user, self.mock_repo, '2024-01-10', '2024-01-01', self.language
        )
        self.assertEqual(status, 400)
        self.assertEqual(response.status, Status.ERROR)

    def test_create_date_exceeded_errors_fields(self):
        errors = controllers.create_date_exceeded_errors(self.language)
        fields = [e.validation_field for e in errors]
        self.assertIn('dateFrom', fields)
        self.assertIn('dateTo', fields)

    def test_process_workout_data(self):
        data = [
            {
                "duration": 105,
                "intensity": 5,
                "mood": "PROUD",
                "sleepScore": 90,
                "startTime": "2025-07-08T15:48:00.00000Z"
            },
            {
                "duration": 20,
                "intensity": 5,
                "mood": "PROUD",
                "sleepScore": 90,
                "startTime": "2025-07-09T14:48:00.00000Z"
            },
            {
                "duration": 20,
                "intensity": 50,
                "mood": "PROUD",
                "sleepScore": 90,
                "startTime": "2025-07-09T14:48:00.00000Z"
            }
        ]
        wrong = []
        accepted = []
        controllers.process_workout_data(
            self.language, data, wrong, accepted)
        self.assertEqual(len(accepted), 2)
        self.assertEqual(len(wrong), 1)

    @patch('src.workouts.application.validations.parse_workout')
    @patch('src.workouts.application.validations.validate_workout')
    def test_process_workout_data_all_errors(self, mock_validate, mock_parse):
        mock_parse.side_effect = [
            (None, self.dummy_warning),
            (None, self.dummy_warning)
        ]
        wrong = []
        accepted = []
        controllers.process_workout_data(
            self.language, [{}, {}], wrong, accepted)
        self.assertEqual(len(accepted), 0)
        self.assertEqual(len(wrong), 2)


if __name__ == "__main__":
    unittest.main()
