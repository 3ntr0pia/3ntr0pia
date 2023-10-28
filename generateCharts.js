
// Import required modules
const fs = require('fs');
const { ChartJSNodeCanvas } = require('chartjs-node-canvas');

// Initialize Chart.js in Node.js
const chartCallback = (ChartJS) => {
  // Customize global settings here, if needed
};
const width = 800;
const height = 600;
const chartJSNodeCanvas = new ChartJSNodeCanvas({ width, height, chartCallback });

// Function to read and parse accumulated.json
const readAccumulatedJson = () => {
  const rawData = fs.readFileSync('accumulated.json');
  return JSON.parse(rawData);
};

// Function to prepare data for charts
const prepareChartData = (accumulatedData) => {
  return {
    languagesData: {
      labels: accumulatedData.languages.map(lang => lang.name),
      datasets: [{
        data: accumulatedData.languages.map(lang => lang.total_seconds / 3600),
      }],
    },
    idesData: {
      labels: accumulatedData.editors.map(editor => editor.name),
      datasets: [{
        data: accumulatedData.editors.map(editor => editor.total_seconds / 3600),
      }],
    }
  };
};

// Function to generate and save charts
const generateAndSaveCharts = async (languagesData, idesData) => {
  const donutConfig = {
    type: 'doughnut',
    data: languagesData,
    // Add other Chart.js options here
  };
  const radarConfig = {
    type: 'radar',
    data: idesData,
    // Add other Chart.js options here
  };

  const donutImage = await chartJSNodeCanvas.renderToBuffer(donutConfig);
  fs.writeFileSync('donutChart.png', donutImage);

  const radarImage = await chartJSNodeCanvas.renderToBuffer(radarConfig);
  fs.writeFileSync('radarChart.png', radarImage);
  
  // Here you can include code to combine both images into a single transparent image.
};

// Main execution
const main = async () => {
  const accumulatedData = readAccumulatedJson();
  const { languagesData, idesData } = prepareChartData(accumulatedData);
  await generateAndSaveCharts(languagesData, idesData);
};

main().catch(console.error);
