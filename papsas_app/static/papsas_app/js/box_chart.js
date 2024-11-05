async function loadEvents() {
    try {
        const response = await fetch('/events/boxplot/');
        const events = await response.json();
  
        const select = document.getElementById('event-select');
  
        events.forEach(event => {
            const option = document.createElement('option');
            option.value = event.id;
            option.textContent = event.name;
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
  
        // Plot the box plot with Plotly
        const plotData = [
            {
                y: data.ratings,
                type: 'box',
                name: data.event.name,
            }
        ];
  
        const layout = {
            title: `Event Ratings: ${data.event.name}`,
            yaxis: { title: 'Rating' },
            height: 300,
            width : 500,
        };
  const config = {
      displayModeBar: true, 
      displaylogo: false, 
      modeBarButtonsToRemove: [
          'hoverClosestCartesian', 'hoverCompareCartesian'
      ],
      modeBarButtons: [['resetScale2d', 'zoomIn2d', 'zoomOut2d', 'toImage' ]],  
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