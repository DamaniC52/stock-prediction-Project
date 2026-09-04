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
import { useChartTheme } from "./useChartTheme";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

const crosshair = {
  id: "crosshair",
  afterDatasetsDraw(chart) {
    const active = chart.tooltip?.getActiveElements?.();
    if (!active?.length) return;

    const { ctx, chartArea } = chart;
    const x = active[0].element.x;

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x, chartArea.top);
    ctx.lineTo(x, chartArea.bottom);
    ctx.lineWidth = 1;
    ctx.strokeStyle = chart.options.plugins.crosshair.color;
    ctx.stroke();
    ctx.restore();
  },
};

function PriceChart({ dates, actual, predicted }) {
  const theme = useChartTheme();

  const data = {
    labels: dates,
    datasets: [
      {
        label: "Actual",
        data: actual,
        borderColor: theme.actual,
        backgroundColor: theme.actual,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBorderWidth: 2,
        pointHoverBorderColor: theme.surface,
        tension: 0.25,
      },
      {
        label: "Predicted",
        data: predicted,
        borderColor: theme.predicted,
        backgroundColor: theme.predicted,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBorderWidth: 2,
        pointHoverBorderColor: theme.surface,
        tension: 0.25,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    layout: { padding: { top: 8 } },
    plugins: {
      crosshair: { color: theme.axis },
      legend: {
        position: "top",
        align: "end",
        labels: {
          boxWidth: 8,
          boxHeight: 8,
          usePointStyle: true,
          pointStyle: "circle",
          color: theme.secondary,
          padding: 16,
          font: { size: 12 },
        },
      },
      tooltip: {
        backgroundColor: theme.surface,
        titleColor: theme.secondary,
        bodyColor: theme.primary,
        borderColor: theme.axis,
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        boxWidth: 8,
        boxHeight: 8,
        usePointStyle: true,
        titleFont: { size: 11, weight: "500" },
        bodyFont: { size: 13 },
        callbacks: {
          label: (item) => ` ${item.dataset.label}  $${item.parsed.y.toFixed(2)}`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        border: { color: theme.axis },
        ticks: {
          color: theme.muted,
          maxTicksLimit: 7,
          maxRotation: 0,
          autoSkipPadding: 16,
          font: { size: 11 },
        },
      },
      y: {
        grid: { color: theme.grid, drawTicks: false },
        border: { display: false, dash: undefined },
        ticks: {
          color: theme.muted,
          padding: 8,
          maxTicksLimit: 6,
          font: { size: 11 },
          callback: (value) => `$${value}`,
        },
      },
    },
  };

  return <Line data={data} options={options} plugins={[crosshair]} />;
}

export default PriceChart;
