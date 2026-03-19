import { useEffect, useState } from "react";

interface Ticket {
  id: string;
  subject: string;
  status: string;
  priority: string | null;
  created_at: string;
}

function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/tickets/")
      .then((res) => res.json())
      .then(setTickets)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Support Ticket Triage
          </h1>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8">
        {loading ? (
          <p className="text-gray-500">Loading tickets...</p>
        ) : tickets.length === 0 ? (
          <p className="text-gray-500">No tickets yet.</p>
        ) : (
          <div className="overflow-hidden rounded-lg bg-white shadow">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Subject
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td className="whitespace-nowrap px-6 py-4 font-medium text-gray-900">
                      {ticket.subject}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4">
                      <span className="inline-flex rounded-full bg-blue-100 px-2 text-xs font-semibold leading-5 text-blue-800">
                        {ticket.status}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-gray-500">
                      {ticket.priority ?? "—"}
                    </td>
                    <td className="whitespace-nowrap px-6 py-4 text-gray-500">
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
