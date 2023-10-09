const ctx = document.getElementById('myBarChart').getContext('2d');

var chartsData = {
    type: 'bar',
    data: {
        labels: ['Visa', 'Master', 'Maestro', 'American Express', 'Cirrus', 'PayPal'],
        datasets: [{
            label: 'Amount ($)',
            data: [0,0,0,0,0,0],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1,
            barPercentage: 0.5
        }]
    },
    options: {
        scales: {
            x: {
                position: 'bottom',
                title: {
                padding: 25,
                display: true,
                text: 'Card Type',
                font: {
                    size: 25
                  }
                }
            }
        }
    }
}

const myBarChart = new Chart(ctx, chartsData);
Chart.defaults.font.weight = 'bold';
Chart.defaults.font.size = 15;

console.log('Hello World!');

var socket = new WebSocket('ws://localhost:8000/ws/charts/')

socket.onmessage = function(e){
    const djangoData = JSON.parse(e.data);
    //console.log(djangoData);

    const chartsData = Object.values(djangoData.sales_data);
    const chartsLabels = Object.values(djangoData.labels);
    console.log(chartsData);
    console.log(chartsLabels);

    const n = 5;

    // looping from i = 0 to 5
    for (let i = 0; i <= n; i++) {
        myBarChart.data.labels[i] = chartsLabels[i]
        myBarChart.data.datasets[0].data[i] = chartsData[i];
    }

    myBarChart.update()

    divElement = document.querySelector('#current_refresh_time')
    if(typeof divElement !== null && divElement !== 'undefined' ) {
      document.querySelector('#current_refresh_time').innerText = djangoData.current_refresh_time;
    }
}