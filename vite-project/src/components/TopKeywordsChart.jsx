import { Bar } from 'react-chartjs-2';
import { Card, CardContent, Typography } from '@mui/material';

const TopKeywordsChart = ({ keywords }) => {
  const chartData = {
    labels: keywords.map(k => k.word), // e.g., ["loan", "rate", "approval"]
    datasets: [
      {
        label: 'Mentions',
        data: keywords.map(k => k.count), // e.g., [15, 10, 8]
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
      },
    ],
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Top Keywords</Typography>
        <Bar data={chartData} />
      </CardContent>
    </Card>
  );
};
export default TopKeywordsChart;
