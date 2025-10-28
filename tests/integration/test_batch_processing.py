"""
Integration tests for batch processing.
Tests the end-to-end batch processing workflow.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch, Mock

from app.services.api_manager import APIManager
from app.services.data_manager import DataManager
from app.ui.components.batch_processor import BatchProcessor


class TestBatchProcessorIntegration:
    """Integration tests for batch processing."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_processing_end_to_end(self, mock_tkinter_root, sample_cells_batch):
        """Test complete batch processing workflow."""
        # Setup
        api_manager = APIManager(api_type="openai", api_key="test-key")
        loop = asyncio.get_event_loop()
        processor = BatchProcessor(mock_tkinter_root, api_manager, loop)

        # Mock API responses
        with patch.object(api_manager, 'process_single_cell') as mock_process:
            mock_process.return_value = (True, "PROCESSED", None)

            # Track progress updates
            progress_updates = []

            def progress_callback(processed, success, error, total, status):
                progress_updates.append({
                    'processed': processed,
                    'success': success,
                    'error': error,
                    'total': total,
                    'status': status
                })

            # Track completion
            completion_called = []

            def completion_callback(results, success_count, error_count):
                completion_called.append({
                    'results': results,
                    'success_count': success_count,
                    'error_count': error_count
                })

            # Process batch
            await processor._process_batches_async(
                cells=sample_cells_batch,
                system_prompt="System",
                user_prompt="Process",
                batch_size=2,
                temperature=0.3,
                max_tokens=100,
                progress_callback=progress_callback,
                completion_callback=completion_callback
            )

            # Verify processing completed
            assert len(completion_called) == 1
            assert completion_called[0]['success_count'] == 4
            assert completion_called[0]['error_count'] == 0

            # Verify all cells were processed
            results = completion_called[0]['results']
            assert len(results) == 4
            assert all(r['success'] for r in results)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_processing_with_errors(self, mock_tkinter_root, sample_cells_batch):
        """Test batch processing with some failures."""
        api_manager = APIManager(api_type="openai", api_key="test-key")
        loop = asyncio.get_event_loop()
        processor = BatchProcessor(mock_tkinter_root, api_manager, loop)

        # Mock API with alternating success/failure
        call_count = [0]

        def mock_process(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] % 2 == 0:
                return False, None, "Error processing"
            return True, "SUCCESS", None

        with patch.object(api_manager, 'process_single_cell', side_effect=mock_process):
            completion_called = []

            def completion_callback(results, success_count, error_count):
                completion_called.append({
                    'results': results,
                    'success_count': success_count,
                    'error_count': error_count
                })

            await processor._process_batches_async(
                cells=sample_cells_batch,
                system_prompt="System",
                user_prompt="Process",
                batch_size=2,
                temperature=0.3,
                max_tokens=100,
                progress_callback=lambda *args: None,
                completion_callback=completion_callback
            )

            # Should have both successes and failures
            assert completion_called[0]['success_count'] == 2
            assert completion_called[0]['error_count'] == 2

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_processing_cancellation(self, mock_tkinter_root, sample_cells_batch):
        """Test cancelling batch processing mid-execution."""
        api_manager = APIManager(api_type="openai", api_key="test-key")
        loop = asyncio.get_event_loop()
        processor = BatchProcessor(mock_tkinter_root, api_manager, loop)

        # Mock API that's slow
        async def slow_process(*args, **kwargs):
            await asyncio.sleep(0.1)
            return True, "RESULT", None

        with patch.object(api_manager, 'process_single_cell', side_effect=slow_process):
            completion_called = []

            def completion_callback(results, success_count, error_count):
                completion_called.append({
                    'results': results,
                    'success_count': success_count
                })

            # Start processing
            task = asyncio.create_task(processor._process_batches_async(
                cells=sample_cells_batch,
                system_prompt="System",
                user_prompt="Process",
                batch_size=1,
                temperature=0.3,
                max_tokens=100,
                progress_callback=lambda *args: None,
                completion_callback=completion_callback
            ))

            # Cancel after a short delay
            await asyncio.sleep(0.05)
            processor.cancel_processing()
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

            # Should have partial results
            if len(completion_called) > 0:
                assert completion_called[0]['success_count'] < 4

    @pytest.mark.integration
    def test_batch_processing_with_context(self, mock_tkinter_root, sample_cells_with_context):
        """Test batch processing with context data."""
        api_manager = APIManager(api_type="openai", api_key="test-key")
        loop = asyncio.get_event_loop()
        processor = BatchProcessor(mock_tkinter_root, api_manager, loop)

        with patch.object(api_manager, 'process_single_cell') as mock_process:
            mock_process.return_value = (True, "PROCESSED", None)

            completion_called = []

            def completion_callback(results, success_count, error_count):
                completion_called.append({
                    'results': results,
                    'success_count': success_count
                })

            # Run synchronously for testing
            async def run_test():
                await processor._process_batches_async(
                    cells=sample_cells_with_context,
                    system_prompt="System",
                    user_prompt="Process",
                    batch_size=2,
                    temperature=0.3,
                    max_tokens=100,
                    progress_callback=lambda *args: None,
                    completion_callback=completion_callback
                )

            loop.run_until_complete(run_test())

            # Verify context was passed to API
            calls = mock_process.call_args_list
            assert len(calls) == 2

            # Check that context_data was passed
            for call in calls:
                args, kwargs = call
                assert 'context_data' in kwargs
                assert 'Name' in kwargs['context_data']


class TestDataManagerBatchUpdate:
    """Integration tests for DataManager batch updates."""

    @pytest.mark.integration
    def test_batch_update_integration(self, sample_dataframe, temp_dir):
        """Test batch updating with DataManager."""
        dm = DataManager()
        dm.df = sample_dataframe

        # Create batch updates
        updates = [
            {'row': 0, 'col': 'Text', 'result': 'Updated 1'},
            {'row': 1, 'col': 'Text', 'result': 'Updated 2'},
            {'row': 2, 'col': 'Text', 'result': 'Updated 3'}
        ]

        success_count, error_count = dm.update_range(updates)

        assert success_count == 3
        assert error_count == 0
        assert dm.df.loc[0, 'Text'] == 'Updated 1'
        assert dm.df.loc[1, 'Text'] == 'Updated 2'
        assert dm.df.loc[2, 'Text'] == 'Updated 3'

    @pytest.mark.integration
    def test_batch_update_with_auto_save(self, sample_csv_file, temp_dir):
        """Test batch update with auto-save enabled."""
        dm = DataManager()
        dm.load_file(str(sample_csv_file))

        output_file = temp_dir / "output.csv"
        dm.file_path = str(output_file)

        updates = [
            {'row': 0, 'col': 'Name', 'result': 'John Smith'},
            {'row': 1, 'col': 'Name', 'result': 'Jane Doe'}
        ]

        # Update with auto_save=True
        success_count, error_count = dm.update_range(updates, auto_save=True)

        assert success_count == 2
        assert output_file.exists()

        # Reload and verify
        dm2 = DataManager()
        dm2.load_file(str(output_file))
        assert dm2.df.loc[0, 'Name'] == 'John Smith'


class TestAPIManagerBatchProcessing:
    """Integration tests for API manager in batch scenarios."""

    @pytest.mark.integration
    @patch('app.services.api_manager.OpenAI')
    def test_rate_limiting_during_batch(self, mock_openai):
        """Test that rate limiting works during batch processing."""
        manager = APIManager(api_key="test-key")

        # Mock response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "result"
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        manager.client = mock_client

        # Set low rate limit
        manager.max_requests_per_minute = 5

        # Process multiple cells
        results = []
        for i in range(7):
            success, result, error = manager.process_single_cell(
                cell_content=f"cell {i}",
                system_prompt="system",
                user_prompt="prompt"
            )
            results.append((success, result, error))

        # First 5 should succeed
        assert all(r[0] for r in results[:5])

        # Next 2 should be rate limited
        assert not results[5][0]
        assert "rate limit" in results[5][2].lower()


class TestEndToEndWorkflow:
    """End-to-end integration tests."""

    @pytest.mark.integration
    @patch('app.services.api_manager.OpenAI')
    def test_complete_workflow_csv(self, mock_openai, sample_csv_file, temp_dir):
        """Test complete workflow: load -> process -> save."""
        # Setup
        dm = DataManager()
        dm.load_file(str(sample_csv_file))

        api_manager = APIManager(api_key="test-key")

        # Mock API
        mock_response = MagicMock()
        mock_choice = MagicMock()

        def get_content():
            return "UPPERCASE"

        mock_choice.message.content = property(lambda self: get_content())
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        api_manager.client = mock_client

        # Get cells to process
        cells = dm.get_range(0, 2, ['Name'])

        # Process each cell
        results = []
        for cell in cells:
            success, result, error = api_manager.process_single_cell(
                cell_content=str(cell['content']),
                system_prompt="System",
                user_prompt="Convert to uppercase"
            )

            if success:
                results.append({
                    'row': cell['row'],
                    'col': cell['col'],
                    'result': result
                })

        # Update data
        dm.update_range(results)

        # Save
        output_file = temp_dir / "output.csv"
        success, error = dm.save_file(str(output_file))

        assert success
        assert output_file.exists()

        # Verify final result
        dm2 = DataManager()
        dm2.load_file(str(output_file))
        assert dm2.df.loc[0, 'Name'] == 'UPPERCASE'

    @pytest.mark.integration
    @patch('app.services.api_manager.requests.post')
    def test_complete_workflow_ollama(self, mock_post, sample_csv_file, temp_dir):
        """Test complete workflow with Ollama."""
        # Setup
        dm = DataManager()
        dm.load_file(str(sample_csv_file))

        api_manager = APIManager(api_type="ollama")

        # Mock Ollama streaming response
        mock_response = Mock()
        mock_response.status_code = 200

        import json
        response_lines = [
            json.dumps({'response': 'lowercase', 'done': True}).encode()
        ]
        mock_response.iter_lines.return_value = response_lines
        mock_post.return_value = mock_response

        # Get cells
        cells = dm.get_range(0, 1, ['Name'])

        # Process
        results = []
        for cell in cells:
            success, result, error = api_manager.process_single_cell(
                cell_content=str(cell['content']),
                system_prompt="System",
                user_prompt="Convert to lowercase"
            )

            if success:
                results.append({
                    'row': cell['row'],
                    'col': cell['col'],
                    'result': result
                })

        # Update and save
        dm.update_range(results)
        output_file = temp_dir / "output_ollama.csv"
        dm.save_file(str(output_file))

        # Verify
        assert output_file.exists()
        dm2 = DataManager()
        dm2.load_file(str(output_file))
        assert dm2.df.loc[0, 'Name'] == 'lowercase'


class TestErrorRecovery:
    """Test error recovery in batch processing."""

    @pytest.mark.integration
    def test_partial_batch_completion(self, sample_dataframe, temp_dir):
        """Test that partial results are saved even if batch is interrupted."""
        dm = DataManager()
        dm.df = sample_dataframe

        # Simulate partial updates
        updates = [
            {'row': 0, 'col': 'Text', 'result': 'Success 1'},
            {'row': 1, 'col': 'Text', 'result': 'Success 2'},
            # Simulate interruption here
        ]

        dm.update_range(updates, auto_save=False)

        # Verify partial results are in memory
        assert dm.df.loc[0, 'Text'] == 'Success 1'
        assert dm.df.loc[1, 'Text'] == 'Success 2'
        assert dm.modified is True

    @pytest.mark.integration
    @patch('app.services.api_manager.OpenAI')
    def test_retry_failed_cells(self, mock_openai, sample_cells_batch):
        """Test retrying failed cell processing."""
        api_manager = APIManager(api_key="test-key")

        # First call fails, second succeeds
        call_count = [0]

        def mock_create(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Temporary failure")

            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_choice.message.content = "success"
            mock_response.choices = [mock_choice]
            return mock_response

        mock_client = MagicMock()
        mock_client.chat.completions.create = mock_create
        api_manager.client = mock_client

        # First attempt fails
        success1, result1, error1 = api_manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )
        assert not success1

        # Retry succeeds
        success2, result2, error2 = api_manager.process_single_cell(
            cell_content="test",
            system_prompt="system",
            user_prompt="prompt"
        )
        assert success2
        assert result2 == "success"
