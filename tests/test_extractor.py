
from etl import extractor
import pytest
from unittest.mock import patch, MagicMock

from etl.extractor import ClickUpExtractor

class TestClickUpExtractor:
    @patch('etl.extractor.requests.get')
    def test_fetch_closed_tasks_success(self, mock_get):
        """Test trường hợp gọi API ClickUp thành công và trả về danh sách task closed."""
        # 1. Chuẩn bị (Arrange)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tasks': [
                {'id': '1', 'name': 'Task 1', 'status': {'status': 'Closed'}},
                {'id': '2', 'name': 'Task 2', 'status': {'status': 'Closed'}}

            ]
        }
        mock_get.return_value = mock_response
        extractor = ClickUpExtractor(api_token = "fake_token", list_id="fake_list")

        # 2. Thực thi (Act)
        tasks = extractor.fetch_closed_tasks()

        # 3. Kiểm tra (Assert)
        assert len(tasks) == 2
        assert tasks[0]['name'] == 'Task 1'
        mock_get.assert_called_once()

    @patch('etl.extractor.requests.get')
    def test_fetch_closed_tasks_failure(self, mock_get):
        """Test trường hợp gọi API ClickUp thất bại (ví dụ sai Token)."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        extractor = ClickUpExtractor(api_token = 'wrong_token', list_id= 'fake_list')

        with pytest.raises(Exception) as excinfo:
            extractor.fetch_closed_tasks()

        assert "Loi goi API" in str(excinfo.value)
            