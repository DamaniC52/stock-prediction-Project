function DataTable({ dates, actual, predicted }) {
  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            <th scope="col">Date</th>
            <th scope="col" className="num">Actual</th>
            <th scope="col" className="num">Predicted</th>
            <th scope="col" className="num">Difference</th>
          </tr>
        </thead>
        <tbody>
          {dates.map((date, i) => {
            const difference = predicted[i] - actual[i];
            return (
              <tr key={date}>
                <td>{date}</td>
                <td className="num">${actual[i].toFixed(2)}</td>
                <td className="num">${predicted[i].toFixed(2)}</td>
                <td className="num">
                  {difference >= 0 ? "+" : "−"}$
                  {Math.abs(difference).toFixed(2)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default DataTable;
