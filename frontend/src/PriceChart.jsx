import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

function PriceChart({ dates, actual, predicted }) {
  const data = {
    labels: dates,
    datasets: [
      {
        label: "Actual",
        data: actual,
        borderColor: "#2563eb",
        backgroundColor: "#2563eb",
        borderWidth: 2,
        pointRadius: 0,
      },
      {
        label: "Predicted",
        data: predicted,
        borderColor: "#f59e0b",
        backgroundColor: "#f59e0b",
        borderWidth: 2,
        pointRadius: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { position: "top" },
    },
    scales: {
      x: { ticks: { maxTicksLimit: 8 } },
      y: { ticks: { callback: (value) => "$" + value } },
    },
  };

  return <Line data={data} options={options} />;
}

export default PriceChart;
