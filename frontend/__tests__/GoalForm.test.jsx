// Tests for GoalForm component
import { render, screen, fireEvent } from '@testing-library/react'
import GoalForm from '../components/GoalForm'

describe('GoalForm', () => {
  it('renders input fields', () => {
    render(<GoalForm onResult={() => {}} />)
    expect(screen.getByLabelText(/Title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument()
  })

  it('submits and shows result via callback', async () => {
    // mock fetch
    global.fetch = jest.fn().mockResolvedValue({ json: async () => ({ task_id: '123', plan: [] }) })
    const onResult = jest.fn()
    render(<GoalForm onResult={onResult} />)
    fireEvent.change(screen.getByLabelText(/Title/i), { target: { value: 'T' } })
    fireEvent.submit(screen.getByRole('button', { name: /submit/i }).closest('form'))
    await Promise.resolve()
    expect(onResult).toHaveBeenCalled()
  })
})
