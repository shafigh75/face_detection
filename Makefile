uploader:
	@echo "***************************************************************"
	@echo "[INFO] uploader launching ..."
	@./fileUploader/mohammad > logger.txt 2>&1 &
	@echo "[INFO] uploader started and the request log file is : logger.txt"
	@echo "[INFO] access the fileUploader at : http://127.0.0.1:5555/upload"
model:
	@echo "***************************************************************"
	@echo "[INFO] model is launching ..."
	@python3 ./image2Encoding/thread.py
start: uploader model 
down:
	@echo "***************************************************************"
	@echo "[INFO] graceful shutdown ..."
	@pkill mohammad
