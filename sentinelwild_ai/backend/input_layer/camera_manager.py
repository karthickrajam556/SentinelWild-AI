import cv2


class CameraManager:
    def __init__(self):
        self.cap = None
        self.is_running = False

    def start_camera(self, source=0):
        if not self.is_running:
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                raise Exception("Unable to access camera")
            self.is_running = True

    def get_frame(self):
        if self.cap and self.is_running:
            success, frame = self.cap.read()
            if success:
                return frame
        return None

    def stop_camera(self):
        if self.cap:
            self.cap.release()
        self.is_running = False
