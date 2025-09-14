async function loadEvents() {
    try {
        const response = await fetch('/events/boxplot/');
        const events = await response.json();
  
        const select = document.getElementById('event-select');
  
        events.forEach(event => {
            const option = document.createElement('option');
            option.value = event.id;
            option.textContent = event.name + " " + event.year;
            select.appendChild(option);
        });
  
        if (events.length > 0) {
            select.value = events[0].id;
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
  }
  
  async function loadBoxPlot() {
    try {
        const select = document.getElementById('event-select');
        const eventId = select.value;
        console.log(eventId)
  
        const response = await fetch(`/get_event/${eventId}/rating/`);
        const data = await response.json();
  
        const plotData = [
            {
                y: data.ratings,
                type: 'box',
                name: data.event.name + " " + data.event.year,
                marker: {
                    color: 'hsl(4.3,100%,59.4%, 0.6)' // Background color for data points
                },
                line: {
                    color: 'hsl(4.3,100%,59.4%, 1)', // Border color for the box
                    width: 3 // Border width
                }
            }
        ];
  
        const layout = {
            yaxis: { title: 'Rating' },
            height: 300,
        };
  const config = {
      displayModeBar: true, 
      displaylogo: false, 
      modeBarButtonsToRemove: [
          'hoverClosestCartesian', 'hoverCompareCartesian', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'toImage'
      ],
      modeBarButtons: [[ ]],  
      modeBarStyle: { position: 'outside' } 
  };
  
        Plotly.newPlot('boxchart-container', plotData, layout, config);
    } catch (error) {
        console.error('Error loading box plot:', error);
    }
  }
  
  async function initPage() {
    await loadEvents();
    await loadBoxPlot();
  }
  
  document.addEventListener('DOMContentLoaded', initPage);