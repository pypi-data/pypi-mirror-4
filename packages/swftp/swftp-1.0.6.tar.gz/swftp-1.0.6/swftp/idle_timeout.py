
class SwiftSSHServerTransport(SSHServerTransport):
    # Overridden to set the version string.
    version = 'SwFTP'
    ourVersionString = 'SSH-2.0-SwFTP'

    def __init__(self):
        self._last_seq_num = 0
        self._idle_failed_count = 0
        self._idle_check = task.LoopingCall(self.__check_idle)
        self._idle_check.start(900)

    def __check_idle(self):
        if self.incomingPacketSequence == self._last_seq_num:
            self._idle_failed_count += 1
            if self._idle_failed_count >= 2:
                self.sendDisconnect(DISCONNECT_CONNECTION_LOST, "idle timeout")
                self._idle_check.stop()
        self._last_seq_num = self.incomingPacketSequence

    def dataReceived(self, data):
        if data.strip() in ['quit', 'exit']:
            self.sendDisconnect(DISCONNECT_CONNECTION_LOST, "exit")
        return SSHServerTransport.dataReceived(self, data)
