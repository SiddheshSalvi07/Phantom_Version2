// Frontend index page: goal form and results display
import Head from 'next/head'
import { useState } from 'react'
import GoalForm from '../components/GoalForm'

export default function Home() {
  const [result, setResult] = useState(null)

  return (
    <div>
      <Head>
        <title>PHANTOM MVP</title>
      </Head>
      <main className="p-8">
        <h1 className="text-2xl font-bold">PHANTOM — MVP</h1>
        <p className="mt-2">Create a goal and see a mocked plan.</p>
        <div className="mt-4">
          <GoalForm onResult={setResult} />
        </div>
        {result && (
          <div className="mt-6 p-4 border rounded">
            <h2 className="font-semibold">Result</h2>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </main>
    </div>
  )
}
