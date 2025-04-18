# Frequently Asked Questions

This document collects common questions and solutions when using the LAN File Transfer Tool.

## Installation Issues

### Q: Errors when installing dependencies

**Problem**: Errors occur when running `pip install -r requirements.txt`.

**Solution**:
1. Make sure you are using Python 3.8 or higher: `python --version`
2. Try updating pip: `pip install --upgrade pip`
3. Use a mirror repository: `pip install -r requirements.txt -i https://pypi.org/simple`
4. If specific dependencies fail to install, try installing them individually and check detailed error messages

### Q: PyWebView installation fails on Windows

**Problem**: When installing PyWebView on Windows, you get a `Microsoft Visual C++ 14.0 or greater is required` error.

**Solution**:
1. Download and install [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Select the "C++ build tools" workload during installation
3. Try installing PyWebView again

## Startup Issues

### Q: Server fails to start

**Problem**: When running `python app.py`, the application fails to start.

**Solution**:
1. Check if port 5000 is already in use:
   - Windows: `netstat -ano | findstr 5000`
   - macOS/Linux: `lsof -i :5000`
2. If the port is in use, you can set `SERVER_PORT=another_port_number` in the `.env` file
3. Check the log output for specific error messages
4. Make sure you have sufficient permissions to run the application

### Q: Cannot access the application after startup

**Problem**: The application starts successfully, but cannot be accessed via a browser.

**Solution**:
1. Make sure the URL you are accessing is correct, including the port number
2. Check firewall settings to ensure the application port is open
3. If using a LAN IP, make sure your device is connected to the same network
4. Try accessing using `localhost` or `127.0.0.1` to verify the server is running properly

## Upload Issues

### Q: Cannot upload large files

**Problem**: Failure when trying to upload large files.

**Solution**:
1. Confirm if the file size exceeds the configured maximum limit (default 5GB)
2. For files larger than 50MB, chunked upload should be used automatically
3. Check if the upload directory has sufficient disk space and write permissions
4. If using chunked upload, ensure the network connection is stable
5. Try increasing the value of the `CHUNK_SIZE` configuration option to reduce the number of chunks

### Q: Upload process interrupted

**Problem**: File upload process is interrupted and cannot complete.

**Solution**:
1. For large files, use the chunked upload feature, which supports resumable uploads
2. Check if the network connection is stable
3. Make sure the browser doesn't automatically refresh or close the page
4. If the upload is paused, you can use the "Resume Upload" feature to continue
5. Check the server logs for possible error causes

### Q: File corrupted after upload

**Problem**: File uploads successfully, but is corrupted or incomplete when downloaded.

**Solution**:
1. Check if there were any error messages during the upload process
2. For large files, make sure all chunks were successfully uploaded
3. Verify that the source file is intact
4. Check if there is sufficient disk space
5. Try uploading again with a smaller chunk size

## Download Issues

### Q: Cannot download files

**Problem**: Nothing happens or an error occurs when clicking the download button.

**Solution**:
1. Make sure the file still exists on the server
2. Check the browser's download settings
3. Try using a different browser
4. Check the browser console for error messages
5. Verify that file permissions are correct

### Q: Download speed is very slow

**Problem**: File download speed is very slow.

**Solution**:
1. Check network connection speed
2. Make sure no other applications are using a lot of bandwidth
3. For large files, consider using other file transfer tools
4. If on a public network, bandwidth may be limited

## Other Issues

### Q: File list does not update

**Problem**: After uploading or deleting files, the file list does not update.

**Solution**:
1. Manually refresh the page
2. Check if the WebSocket connection is working properly
3. Add `force_refresh=true` to the URL parameters to force cache refresh
4. Restart the application

### Q: Application uses too much memory

**Problem**: The application uses a lot of memory after running for a while.

**Solution**:
1. Check if there are many concurrent upload/download operations
2. Regularly clean the temporary files directory
3. Adjust the `TEMP_FILES_MAX_AGE` configuration option to reduce temporary file retention time
4. Restart the application to release memory

### Q: How to backup uploaded files

**Problem**: Want to backup all uploaded files.

**Solution**:
1. Simply copy the directory specified by the `UPLOAD_FOLDER` configuration option (default is `uploads/`)
2. Use scheduled tasks to automatically backup this directory
3. Consider using cloud storage services for backup

## Contact Support

If your issue is not listed in this document, please get support through the following channels:

1. Submit an issue on [GitHub Issues](https://github.com/MagicCD/Transfer/issues)
2. Check the [Project Wiki](https://github.com/MagicCD/Transfer/wiki) for more information
3. Contact the developer: [CSDN Blog](https://blog.csdn.net/qq_52357217)
