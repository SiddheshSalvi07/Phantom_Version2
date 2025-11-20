// VoiceButton: stub UI element for future STT integration
export default function VoiceButton({ onClick }) {
  return (
    <button type="button" className="px-3 py-2 border rounded" onClick={onClick} aria-label="voice-button">
      🎤 Voice (stub)
    </button>
  )
}
