document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    
    // DOM 元素
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const selectedFilesContainer = document.getElementById('selectedFilesContainer');
    const selectedFilesCount = document.getElementById('selectedFilesCount');
    const selectedFilesList = document.getElementById('selectedFilesList').querySelector('ul');
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressPercent = document.getElementById('progressPercent');
    const progressSize = document.getElementById('progressSize');
    const fileList = document.getElementById('fileList');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const uploadSection = document.getElementById('uploadSection');
    const toast = document.getElementById('toast');
    const pauseResumeBtn = document.getElementById('pauseResumeBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    
    // 保存当前活动的XHR请求，用于取消上传
    let activeXHR = null;
    let isCancelled = false;
    let isPaused = false;
    let isUploading = false;
    let currentFileIndex = 0;  // 添加为全局变量
    let currentPauseResumeBtn = null; // 当前文件的暂停/恢复按钮
    
    // 用于保存暂停状态的信息
    let pauseInfo = {
        file: null,
        fileIndex: 0,
        chunkIndex: 0,
        uploadedSize: 0,
        chunkUploadedSize: 0
    };
    
    // 选择文件事件
    fileInput.addEventListener('change', function() {
        handleSelectedFiles(this.files);
    });
    
    // 处理选择的文件
    function handleSelectedFiles(files) {
        if (files.length > 0) {
            selectedFilesContainer.style.display = 'block';
            selectedFilesCount.textContent = `已选择 ${files.length} 个文件`;
            selectedFilesList.innerHTML = '';
            
            // 创建一个可以被修改的文件列表（FileList对象是只读的）
            const fileArray = Array.from(files);
            
            updateSelectedFilesList(fileArray);
            
            uploadBtn.disabled = false;
        } else {
            selectedFilesContainer.style.display = 'none';
            uploadBtn.disabled = true;
        }
    }
    
    // 更新选中的文件列表UI
    function updateSelectedFilesList(fileArray) {
        selectedFilesList.innerHTML = '';
        selectedFilesCount.textContent = `已选择 ${fileArray.length} 个文件`;
        
        for (let i = 0; i < fileArray.length; i++) {
            const file = fileArray[i];
            const li = document.createElement('li');
            let actionsHTML = '';
            // Only add remove button if upload is NOT in progress
            if (!isUploading) {
                actionsHTML = `
                    <span class="remove-file" data-index="${i}">
                        <i class="fas fa-times"></i>
                    </span>
                `;
            }
            
            li.innerHTML = `
                <span>${file.name} (${formatFileSize(file.size)})</span>
                <div class="file-actions">
                    ${actionsHTML}
                </div>
            `;
            selectedFilesList.appendChild(li);
        }
        
        if (fileArray.length === 0) {
            selectedFilesContainer.style.display = 'none';
            uploadBtn.disabled = true;
            // 重置文件输入框，否则无法重新选择相同的文件
            fileInput.value = '';
        }
    }
    
    // 绑定移除文件事件 (移除了暂停/恢复逻辑)
    selectedFilesList.addEventListener('click', function(e) {
        // 处理移除文件
        const removeBtn = e.target.closest('.remove-file');
        if (removeBtn) {
            const index = parseInt(removeBtn.getAttribute('data-index'));
            
            // 创建一个新的文件数组，排除要删除的文件
            const currentFiles = Array.from(fileInput.files);
            const updatedFiles = currentFiles.filter((_, i) => i !== index);
            
            // 更新UI
            updateSelectedFilesList(updatedFiles);
            
            // 由于无法直接修改fileInput.files，我们需要创建一个新的DataTransfer对象
            const dataTransfer = new DataTransfer();
            updatedFiles.forEach(file => dataTransfer.items.add(file));
            
            // 使用新的DataTransfer对象更新fileInput.files
            fileInput.files = dataTransfer.files;
        }
    });
    
    // 上传按钮点击事件
    uploadBtn.addEventListener('click', function() {
        if (isUploading) {
            // 如果正在上传，则取消上传
            cancelUpload();
        } else if (fileInput.files.length > 0) {
            // 否则开始上传
            uploadFiles(Array.from(fileInput.files));
        }
    });
    
    // 暂停/恢复按钮点击事件
    pauseResumeBtn.addEventListener('click', function() {
        const status = this.getAttribute('data-status');
        if (status === 'pause') {
            pauseUpload();
            this.innerHTML = '<i class="fas fa-play"></i>&nbsp; 继续';
            this.setAttribute('data-status', 'resume');
            this.classList.add('resume-btn');
            this.classList.remove('pause-btn');
        } else {
            resumeUpload();
            this.innerHTML = '<i class="fas fa-pause"></i>&nbsp; 暂停';
            this.setAttribute('data-status', 'pause');
            this.classList.add('pause-btn');
            this.classList.remove('resume-btn');
        }
        currentPauseResumeBtn = this;
    });
    
    // 取消按钮点击事件
    cancelBtn.addEventListener('click', function() {
        if (confirm('确定要取消当前上传吗？')) {
            cancelUpload();
        }
    });
    
    // 上传文件
    function uploadFiles(files) {
        if (files.length === 0) {
            return;
        }
        
        // 如果是恢复上传，需要特殊处理
        const isResuming = isPaused && pauseInfo.file;
        
        // 准备上传
        if (!isResuming) {
            // 显示进度条
            progressContainer.style.display = 'block';
            // 设置上传按钮为取消状态
            uploadBtn.innerHTML = '<i class="fas fa-times"></i>&nbsp; 取消上传';
            uploadBtn.className = 'cancel-upload-btn';
            
            // 重置暂停/恢复按钮状态
            pauseResumeBtn.innerHTML = '<i class="fas fa-pause"></i>&nbsp; 暂停';
            pauseResumeBtn.setAttribute('data-status', 'pause');
            pauseResumeBtn.classList.add('pause-btn');
            pauseResumeBtn.classList.remove('resume-btn');
            currentPauseResumeBtn = pauseResumeBtn;
        } else {
            // 是恢复上传，不重置按钮状态
            // ...保持现有逻辑
        }
        
        // 重置状态
        isCancelled = false;
        isPaused = false;
        isUploading = true; // Set upload status to true
        
        // Update the selected file list to remove the 'X' buttons
        updateSelectedFilesList(files);
        
        // 计算文件总大小
        let totalSize = 0;
        for (let i = 0; i < files.length; i++) {
            totalSize += files[i].size;
        }
        
        // 已上传大小
        let uploadedSize = isResuming ? pauseInfo.uploadedSize : 0;
        
        // 设置初始进度条状态
        if (isResuming && uploadedSize > 0) {
            const resumePercentage = Math.round((uploadedSize / totalSize) * 100);
            progressFill.style.width = `${resumePercentage}%`;
            progressPercent.textContent = `${resumePercentage}%`;
            progressSize.textContent = `${formatFileSize(uploadedSize)} / ${formatFileSize(totalSize)}`;
        }
        
        // 循环上传每个文件
        currentFileIndex = isResuming ? pauseInfo.fileIndex : 0;
        
        function uploadNextFile() {
            if (currentFileIndex >= files.length || isCancelled) {
                // 所有文件上传完成或上传被取消
                if (!isCancelled) {
                    showToast('上传完成!', 'success');
                }
                resetUploadUI();
                isUploading = false;
                return;
            }
            
            if (isPaused) {
                console.log("上传暂停，当前文件索引:", currentFileIndex);
                // 保存当前状态以供恢复
                pauseInfo.file = files[currentFileIndex];
                pauseInfo.fileIndex = currentFileIndex;
                pauseInfo.uploadedSize = uploadedSize;
                return;
            }
            
            const file = files[currentFileIndex];
            // 设置当前上传的文件名为进度条容器的数据属性
            progressContainer.setAttribute('data-filename', file.name);
            
            // 为大文件使用分块上传
            const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB 分块
            
            // 如果文件小于 50MB，使用普通上传
            if (file.size < 50 * 1024 * 1024) {
                uploadWholeFile(file);
            } else {
                uploadLargeFile(file);
            }
        }

        // 常规方式上传整个文件（小文件）
        function uploadWholeFile(file) {
            console.log("小文件上传", file.name, "文件大小:", formatFileSize(file.size));
            
            // 创建 FormData
            const formData = new FormData();
            formData.append('file', file);
            
            // 创建 XMLHttpRequest
            const xhr = new XMLHttpRequest();
            activeXHR = xhr; // 保存当前活动的XHR请求
            
            // 进度事件
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable && !isPaused && !isCancelled) {
                    // 当前文件的上传进度
                    const currentProgress = e.loaded;
                    
                    // 更新总进度
                    const overallProgress = uploadedSize + currentProgress;
                    const percentage = Math.round((overallProgress / totalSize) * 100);
                    
                    // 保存当前进度以支持断点续传
                    pauseInfo.uploadedSize = uploadedSize;
                    
                    // 更新进度条
                    progressFill.style.width = `${percentage}%`;
                    progressPercent.textContent = `${percentage}%`;
                    progressSize.textContent = `${formatFileSize(overallProgress)} / ${formatFileSize(totalSize)}`;
                    
                    // 通过 Socket.IO 发送进度信息
                    socket.emit('upload_progress', {
                        filename: file.name,
                        progress: percentage,
                        loaded: formatFileSize(overallProgress),
                        total: formatFileSize(totalSize)
                    });
                }
            });
            
            // 完成事件
            xhr.addEventListener('load', function() {
                // 清空当前活动XHR
                activeXHR = null;
                
                if (xhr.status === 200 && !isCancelled) {
                    // 更新已上传大小
                    uploadedSize += file.size;
                    
                    // 上传下一个文件
                    currentFileIndex++;
                    uploadNextFile();
                } else if (!isCancelled) {
                    showToast(`上传失败: ${xhr.statusText}`, 'error');
                    resetUploadUI();
                    isUploading = false;
                }
            });
            
            // 错误事件
            xhr.addEventListener('error', function() {
                // 清空当前活动XHR
                activeXHR = null;
                if (!isCancelled) {
                    showToast('网络错误，上传失败', 'error');
                    resetUploadUI();
                    isUploading = false;
                }
            });
            
            // 取消事件
            xhr.addEventListener('abort', function() {
                // 清空当前活动XHR
                activeXHR = null;
            });
            
            // 发送请求
            xhr.open('POST', '/upload');
            xhr.send(formData);
        }

        // 分块上传大文件
        function uploadLargeFile(file) {
            const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB 分块
            const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
            
            // 从暂停位置恢复
            const isResuming = pauseInfo.file && pauseInfo.file.name === file.name;
            let chunkIndex = isResuming ? pauseInfo.chunkIndex : 0;
            let chunkUploadedSize = isResuming ? pauseInfo.chunkUploadedSize : 0;
            
            console.log("大文件上传", isResuming ? "恢复上传" : "开始上传", 
                       "文件:", file.name,
                       "当前块:", chunkIndex, 
                       "总块数:", totalChunks,
                       "已上传块大小:", formatFileSize(chunkUploadedSize));
            
            // 首先检查服务器端的上传状态，确保不是暂停状态
            fetch(`/upload_state/${encodeURIComponent(file.name)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.paused) {
                            console.log("服务器端文件处于暂停状态，需要先恢复");
                            // 可能需要自动恢复或提示用户手动恢复
                            showToast("此文件在服务器端处于暂停状态，请先点击恢复按钮", "error");
                            isPaused = true;
                            if (currentPauseResumeBtn) {
                                currentPauseResumeBtn.innerHTML = '<i class="fas fa-play"></i>';
                                currentPauseResumeBtn.setAttribute('data-status', 'resume');
                            }
                            return;
                        }
                        
                        // 如果服务器有更新的块索引信息，使用服务器的信息
                        if (data.last_chunk > chunkIndex) {
                            console.log(`使用服务器保存的块索引: ${data.last_chunk}`);
                            chunkIndex = data.last_chunk;
                            // 更新暂停信息
                            pauseInfo.chunkIndex = chunkIndex;
                        }
                        
                        // 继续上传
                        uploadNextChunk();
                    } else {
                        console.error("获取上传状态失败:", data.error);
                        uploadNextChunk(); // 仍然尝试上传
                    }
                })
                .catch(error => {
                    console.error("检查上传状态时出错:", error);
                    uploadNextChunk(); // 出错时仍然尝试上传
                });
            
            function uploadNextChunk() {
                if (chunkIndex >= totalChunks || isCancelled) {
                    // 所有块上传完成或上传被取消
                    activeXHR = null;
                    return;
                }
                
                if (isPaused) {
                    // 保存当前状态以供恢复
                    console.log("分块上传暂停，当前块索引:", chunkIndex, "已上传块大小:", formatFileSize(chunkUploadedSize));
                    pauseInfo.chunkIndex = chunkIndex;
                    pauseInfo.chunkUploadedSize = chunkUploadedSize;
                    pauseInfo.file = file;
                    pauseInfo.fileIndex = currentFileIndex;
                    return;
                }
                
                const start = chunkIndex * CHUNK_SIZE;
                const end = Math.min(file.size, start + CHUNK_SIZE);
                const chunk = file.slice(start, end);
                
                console.log(`上传第 ${chunkIndex+1}/${totalChunks} 块, 大小: ${formatFileSize(chunk.size)}`);
                
                // 创建 FormData 对象
                const formData = new FormData();
                formData.append('file', chunk);
                formData.append('filename', file.name);
                formData.append('chunk_number', chunkIndex);
                formData.append('total_chunks', totalChunks);
                
                // 创建 XMLHttpRequest
                const xhr = new XMLHttpRequest();
                activeXHR = xhr; // 保存当前活动的XHR请求
                
                // 上传进度事件
                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable && !isPaused && !isCancelled) {
                        // 当前块的上传进度
                        const currentChunkProgress = e.loaded;
                        
                        // 更新整体进度
                        const fileProgress = chunkUploadedSize + currentChunkProgress;
                        const overallProgress = uploadedSize + fileProgress;
                        const percentage = Math.round((overallProgress / totalSize) * 100);
                        
                        // 保存当前进度信息用于恢复
                        pauseInfo.uploadedSize = uploadedSize;
                        
                        // 更新进度条
                        progressFill.style.width = `${percentage}%`;
                        progressPercent.textContent = `${percentage}%`;
                        progressSize.textContent = `${formatFileSize(overallProgress)} / ${formatFileSize(totalSize)}`;
                        
                        // 通过 Socket.IO 发送进度信息
                        socket.emit('upload_progress', {
                            filename: file.name,
                            progress: percentage,
                            loaded: formatFileSize(overallProgress),
                            total: formatFileSize(totalSize)
                        });
                    }
                });
                
                // 完成事件
                xhr.addEventListener('load', function() {
                    if (isCancelled) {
                        activeXHR = null;
                        return;
                    }
                    
                    if (xhr.status === 200) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            
                            if (response.success) {
                                // 更新已上传的块大小
                                chunkUploadedSize += chunk.size;
                                
                                // 保存进度信息，以便恢复时使用
                                pauseInfo.chunkIndex = chunkIndex + 1; // 下一个块的索引
                                pauseInfo.chunkUploadedSize = chunkUploadedSize;
                                pauseInfo.file = file;
                                pauseInfo.fileIndex = currentFileIndex;
                                pauseInfo.uploadedSize = uploadedSize;
                                
                                // 如果是最后一个块或全部块已上传
                                if (response.status === 'completed') {
                                    console.log(`文件 ${file.name} 上传完成`);
                                    // 更新已上传总大小
                                    uploadedSize += file.size;
                                    
                                    // 上传下一个文件
                                    currentFileIndex++;
                                    activeXHR = null;
                                    uploadNextFile();
                                } else {
                                    // 上传下一个块
                                    console.log(`块 ${chunkIndex+1}/${totalChunks} 上传完成，进度: ${Math.round((chunkUploadedSize / file.size) * 100)}%`);
                                    chunkIndex++;
                                    uploadNextChunk();
                                }
                            } else {
                                // 检查是否是因为暂停而被拒绝
                                if (response.paused) {
                                    console.log("服务器拒绝上传，原因: 已暂停");
                                    isPaused = true;
                                    if (currentPauseResumeBtn) {
                                        currentPauseResumeBtn.innerHTML = '<i class="fas fa-play"></i>';
                                        currentPauseResumeBtn.setAttribute('data-status', 'resume');
                                    }
                                    showToast("上传已暂停，点击恢复按钮继续", "success");
                                } else {
                                    showToast(`上传失败: ${response.error}`, 'error');
                                    resetUploadUI();
                                    isUploading = false;
                                }
                                activeXHR = null;
                            }
                        } catch (e) {
                            showToast('上传失败: 无效的服务器响应', 'error');
                            resetUploadUI();
                            isUploading = false;
                            activeXHR = null;
                        }
                    } else {
                        showToast(`上传失败: ${xhr.statusText}`, 'error');
                        resetUploadUI();
                        isUploading = false;
                        activeXHR = null;
                    }
                });
                
                // 错误事件
                xhr.addEventListener('error', function() {
                    activeXHR = null;
                    if (!isCancelled) {
                        showToast('网络错误，上传失败', 'error');
                        resetUploadUI();
                        isUploading = false;
                    }
                });
                
                // 取消事件
                xhr.addEventListener('abort', function() {
                    activeXHR = null;
                });
                
                // 发送请求
                xhr.open('POST', '/upload/chunk');
                xhr.send(formData);
            }
        }
        
        // 开始上传第一个文件
        uploadNextFile();
    }
    
    // 暂停上传
    function pauseUpload() {
        if (isUploading) {
            console.log("执行暂停上传操作，当前XHR状态:", !!activeXHR);
            // 先设置状态标志再中止请求
            isPaused = true;
            
            // 保存当前文件信息，确保能够从正确位置恢复
            if (fileInput.files.length > currentFileIndex) {
                pauseInfo.file = fileInput.files[currentFileIndex];
                pauseInfo.fileIndex = currentFileIndex;
                // 其他状态(uploadedSize,chunkIndex等)在各自的进度回调中已更新
                
                console.log("暂停上传状态:", {
                    文件: pauseInfo.file ? pauseInfo.file.name : "无",
                    文件索引: pauseInfo.fileIndex,
                    分块索引: pauseInfo.chunkIndex,
                    已上传大小: formatFileSize(pauseInfo.uploadedSize),
                    已上传块大小: formatFileSize(pauseInfo.chunkUploadedSize)
                });
            }
            
            // 更新主暂停/恢复按钮的状态
            const mainPauseResumeBtn = document.querySelector('#pauseResumeBtn'); // Select the main button
            if (mainPauseResumeBtn) { // Check if the main button exists
                mainPauseResumeBtn.innerHTML = '<i class="fas fa-play"></i>&nbsp; 继续';
                mainPauseResumeBtn.setAttribute('data-status', 'resume');
                mainPauseResumeBtn.classList.remove('pause-btn');
                mainPauseResumeBtn.classList.add('resume-btn');
            }
            
            // 中止当前上传请求
            if (activeXHR) {
                activeXHR.abort();
                activeXHR = null;
            }
            
            // 向服务器发送暂停请求，保存暂停状态
            if (pauseInfo.file) {
                fetch(`/pause_upload/${encodeURIComponent(pauseInfo.file.name)}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        chunk_index: pauseInfo.chunkIndex || 0
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log("服务器确认暂停上传:", data.message);
                        // No longer need to update individual file buttons here
                    } else {
                        console.error("暂停上传失败:", data.error);
                    }
                })
                .catch(error => {
                    console.error("发送暂停请求时出错:", error);
                });
            }
            
            showToast('上传已暂停', 'success');
        }
    }
    
    // 恢复上传
    function resumeUpload() {
        if (isPaused && pauseInfo.file) {
            console.log("执行恢复上传操作", {
                文件: pauseInfo.file ? pauseInfo.file.name : "无",
                文件索引: pauseInfo.fileIndex,
                分块索引: pauseInfo.chunkIndex,
                已上传大小: formatFileSize(pauseInfo.uploadedSize),
                已上传块大小: formatFileSize(pauseInfo.chunkUploadedSize)
            });
            
            // 更新主暂停/恢复按钮的状态
            const mainPauseResumeBtn = document.querySelector('#pauseResumeBtn'); // Select the main button
            if (mainPauseResumeBtn) { // Check if the main button exists
                mainPauseResumeBtn.innerHTML = '<i class="fas fa-pause"></i>&nbsp; 暂停';
                mainPauseResumeBtn.setAttribute('data-status', 'pause');
                mainPauseResumeBtn.classList.add('pause-btn');
                mainPauseResumeBtn.classList.remove('resume-btn');
            }
            
            // 向服务器发送恢复请求
            fetch(`/resume_upload/${encodeURIComponent(pauseInfo.file.name)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("服务器确认恢复上传:", data.message, "从块:", data.last_chunk);
                    // 如果服务器保存了上次上传的块索引，可以更新本地状态
                    if (data.last_chunk !== undefined && data.last_chunk !== null) {
                        pauseInfo.chunkIndex = data.last_chunk;
                    }
                    
                    // No longer need to update individual file buttons here
                    
                    // 先保持isPaused为true，让uploadFiles函数能识别这是一个恢复操作
                    isPaused = false; // Set isPaused to false *before* calling uploadFiles
                    // 继续从暂停的位置上传文件
                    const files = Array.from(fileInput.files);
                    uploadFiles(files);
                    
                    showToast('继续上传', 'success');
                } else {
                    console.error("恢复上传失败:", data.error);
                    showToast('恢复上传失败', 'error');
                }
            })
            .catch(error => {
                console.error("发送恢复请求时出错:", error);
                showToast('恢复上传请求失败', 'error');
            });
        }
    }
    
    // 取消上传
    function cancelUpload() {
        if (activeXHR || isPaused) {
            isCancelled = true;
            
            if (activeXHR) {
                activeXHR.abort(); // 取消当前活动的XHR请求
            }
            
            // 通知服务器清理临时文件
            const uploadingFileName = document.querySelector('#progressContainer').getAttribute('data-filename');
            if (uploadingFileName) {
                fetch(`/cancel_upload/${encodeURIComponent(uploadingFileName)}`, {
                    method: 'POST'
                }).catch(error => {
                    console.error('无法通知服务器取消上传:', error);
                });
            }
            
            showToast('上传已取消', 'error');
            resetUploadUI();
            isUploading = false;
            isPaused = false;
            
            // 重置暂停信息
            pauseInfo = {
                file: null,
                fileIndex: 0,
                chunkIndex: 0,
                uploadedSize: 0,
                chunkUploadedSize: 0
            };
        }
    }
    
    // 重置上传 UI
    function resetUploadUI() {
        fileInput.value = '';
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-upload"></i>&nbsp; 上传文件';
        uploadBtn.className = 'upload-btn';
        selectedFilesContainer.style.display = 'none';
        progressContainer.style.display = 'none';
        activeXHR = null;
        isCancelled = false;
        isPaused = false;
        
        // 重置主暂停/恢复按钮状态
        const mainPauseResumeBtn = document.querySelector('#pauseResumeBtn');
        if (mainPauseResumeBtn) {
            mainPauseResumeBtn.innerHTML = '<i class="fas fa-pause"></i>&nbsp; 暂停';
            mainPauseResumeBtn.setAttribute('data-status', 'pause');
            mainPauseResumeBtn.classList.add('pause-btn');
            mainPauseResumeBtn.classList.remove('resume-btn');
        }
        currentPauseResumeBtn = null; // This variable might be removable now
        
        // 重置暂停信息
        pauseInfo = {
            file: null,
            fileIndex: 0,
            chunkIndex: 0,
            uploadedSize: 0,
            chunkUploadedSize: 0
        };
    }
    
    // 文件删除事件委托
    fileList.addEventListener('click', function(e) {
        // 查找最近的删除按钮
        const deleteBtn = e.target.closest('.delete-btn');
        if (deleteBtn) {
            const filename = deleteBtn.getAttribute('data-filename');
            if (confirm(`确定要删除文件 "${filename}" 吗？`)) {
                deleteFile(filename);
            }
        }
    });
    
    // 删除文件
    function deleteFile(filename) {
        fetch(`/delete/${filename}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('文件已删除', 'success');
            } else {
                showToast(`删除失败: ${data.error}`, 'error');
            }
        })
        .catch(error => {
            showToast(`网络错误: ${error.message}`, 'error');
        });
    }
    
    // 清空所有文件
    clearAllBtn.addEventListener('click', function() {
        if (confirm('确定要删除所有文件吗？此操作无法撤销。')) {
            fetch('/delete_all', {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('所有文件已删除', 'success');
                    clearAllBtn.disabled = true;
                } else {
                    showToast(`操作失败: ${data.error}`, 'error');
                }
            })
            .catch(error => {
                showToast(`网络错误: ${error.message}`, 'error');
            });
        }
    });
    
    // 监听文件列表更新
    socket.on('files_updated', function(data) {
        updateFileList(data.files);
    });
    
    // 监听上传进度更新
    socket.on('upload_progress_update', function(data) {
        console.log('收到进度更新:', data);
    });
    
    // 监听上传状态更新事件
    socket.on('upload_state_updated', function(data) {
        console.log('上传状态更新:', data);
        const filename = data.filename;
        const status = data.status;
        const isPausedUpdate = data.paused; // Renamed to avoid conflict with global isPaused
        
        // 如果当前正在上传的文件状态变更，也更新全局状态和进度条上的按钮
        if (isUploading && pauseInfo.file && pauseInfo.file.name === filename) {
            isPaused = isPausedUpdate; // Update the global isPaused state
            const mainPauseResumeBtn = document.querySelector('#pauseResumeBtn');
            if (mainPauseResumeBtn) {
                if (isPausedUpdate) {
                    mainPauseResumeBtn.innerHTML = '<i class="fas fa-play"></i>&nbsp; 继续';
                    mainPauseResumeBtn.setAttribute('data-status', 'resume');
                    mainPauseResumeBtn.classList.remove('pause-btn');
                    mainPauseResumeBtn.classList.add('resume-btn');
                } else {
                    mainPauseResumeBtn.innerHTML = '<i class="fas fa-pause"></i>&nbsp; 暂停';
                    mainPauseResumeBtn.setAttribute('data-status', 'pause');
                    mainPauseResumeBtn.classList.add('pause-btn');
                    mainPauseResumeBtn.classList.remove('resume-btn');
                }
            }
        }
    });
    
    // 更新文件列表
    function updateFileList(files) {
        fileList.innerHTML = '';
        
        if (files && files.length > 0) {
            clearAllBtn.disabled = false;
            
            files.forEach(file => {
                const li = document.createElement('li');
                li.className = 'file-item';
                
                li.innerHTML = `
                    <div class="file-info">
                        <i class="fas ${file.icon} file-icon"></i>
                        <div>
                            ${file.name}<br>
                            <small>${file.size_formatted}</small>
                        </div>
                    </div>
                    <div class="file-actions">
                        <a href="/download/${file.name}" class="action-btn download-btn">
                            <i class="fas fa-download"></i>&nbsp; 下载
                        </a>
                        <button class="action-btn delete-btn" data-filename="${file.name}">
                            <i class="fas fa-trash"></i>&nbsp; 删除
                        </button>
                    </div>
                `;
                
                fileList.appendChild(li);
            });
        } else {
            clearAllBtn.disabled = true;
            
            const li = document.createElement('li');
            li.className = 'no-files';
            li.textContent = '暂无分享文件';
            fileList.appendChild(li);
        }
    }
    
    // 显示提示消息
    function showToast(message, type) {
        toast.textContent = message;
        toast.className = `toast ${type}`;
        
        // 显示提示
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // 3秒后隐藏
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
    
    // 格式化文件大小
    function formatFileSize(bytes) {
        if (bytes < 1024) {
            return bytes + ' B';
        } else if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(2) + ' KB';
        } else if (bytes < 1024 * 1024 * 1024) {
            return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        } else {
            return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
        }
    }
    
    // 拖放文件上传
    function setupDragDrop() {
        // 阻止默认拖放行为
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadSection.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // 高亮显示拖放区域
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadSection.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadSection.addEventListener(eventName, unhighlight, false);
        });
        
        // 处理拖放的文件
        uploadSection.addEventListener('drop', handleDrop, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight() {
            uploadSection.classList.add('drag-highlight');
        }
        
        function unhighlight() {
            uploadSection.classList.remove('drag-highlight');
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            handleSelectedFiles(files);
        }
    }
    
    // 设置拖放功能
    setupDragDrop();
}); 