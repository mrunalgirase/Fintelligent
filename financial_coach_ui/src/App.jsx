import FinancialCoach from './components/FinancialCoach'

function App() {
    return (
        <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
            <header className="max-w-7xl mx-auto mb-12 text-center">
                <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight sm:text-5xl">
                    Fintelligent <span className="text-blue-600">Coach</span>
                </h1>
                <p className="mt-4 text-xl text-gray-500">
                    Your personal India-focused financial guide.
                </p>
            </header>
            <main>
                <FinancialCoach />
            </main>
        </div>
    )
}

export default App
