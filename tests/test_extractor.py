import pytest
from unittest.mock import patch, MagicMock
from etl.extractor import ClickUpExtractor

class TestClickUpExtractor:
    
    @patch('etl.extractor.requests.get')
    def test_fetch_task_details_success(self, mock_get):
        # Thiết lập Mock Response cho request.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "123",
            "name": "Test Task",
            "custom_fields": []
        }
        mock_get.return_value = mock_response
        
        extractor = ClickUpExtractor("fake_token", "fake_team")
        task = extractor.fetch_task_details("123")
        
        assert task["id"] == "123"
        assert task["name"] == "Test Task"
        mock_get.assert_called_once()
        
    @patch('etl.extractor.requests.get')
    def test_fetch_task_details_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        extractor = ClickUpExtractor("fake_token", "fake_team")
        with pytest.raises(Exception) as exc_info:
            extractor.fetch_task_details("123")
            
        assert "Không thể lấy thông tin task 123: 404" in str(exc_info.value)

    @patch('etl.extractor.requests.get')
    def test_fetch_all_workspace_tasks_pagination(self, mock_get):
        # Trả về 2 trang dữ liệu. Trang 1: 100 tasks, Trang 2: 50 tasks.
        def mock_get_behavior(*args, **kwargs):
            page = kwargs['params']['page']
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            
            if page == 0:
                mock_resp.json.return_value = {"tasks": [{"id": str(i)} for i in range(100)]}
            elif page == 1:
                mock_resp.json.return_value = {"tasks": [{"id": str(i)} for i in range(100, 150)]}
            else:
                mock_resp.json.return_value = {"tasks": []}
                
            return mock_resp
            
        mock_get.side_effect = mock_get_behavior
        
        extractor = ClickUpExtractor("fake_token", "fake_team")
        all_tasks = extractor.fetch_all_workspace_tasks()
        
        assert len(all_tasks) == 150
        assert mock_get.call_count == 2