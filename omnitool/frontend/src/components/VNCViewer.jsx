import '../styles/VNCViewer.css'

function VNCViewer({ windowsHostUrl }) {
  const vncUrl = `http://${windowsHostUrl}/vnc.html?view_only=1&autoconnect=1&resize=scale`

  return (
    <div className="vnc-container">
      <div className="vnc-header">
        <h2>🖥️ Windows VM</h2>
      </div>
      <div className="vnc-viewer">
        <iframe
          src={vncUrl}
          title="Windows VM Viewer"
          allow="fullscreen"
        />
      </div>
    </div>
  )
}

export default VNCViewer
