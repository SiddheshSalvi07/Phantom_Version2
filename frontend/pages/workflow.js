// Workflow canvas placeholder page
import WorkflowCanvas from '../components/WorkflowCanvas'

export default function Workflow() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Workflow Canvas (Stub)</h1>
      <p className="mt-2">This is a placeholder for the workflow visualization.</p>
      <div className="mt-4">
        <WorkflowCanvas />
      </div>
    </div>
  )
}
