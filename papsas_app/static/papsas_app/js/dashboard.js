function attendance_day() {
    fetch('/attendance-by-day/')
    .then(response => response.json())
    .then(data => {
      // Extract the day names and attendance counts
      const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
      const attendanceCounts = data.map(item => item.count);
  
      // Create the chart
      const ctx = document.getElementById('attendanceChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: dayNames,
          datasets: [{
            label: 'Attendance Count',
            data: attendanceCounts,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              precision: 0
            }
          },
          plugins: {
            title: {
              display: true,
              text: 'Attendance per Day'
            }
          }
        }
      });
    })
    .catch(error => console.error('Error fetching attendance data:', error));
}

function getTop3Events() {
    fetch('/top_3_events/')
      .then(response => response.json())
      .then(data => {
        const eventNames = data.map(item => item.eventName);
        const attendanceCounts = data.map(item => item.attendanceCount);
  
        const ctx = document.getElementById('top3EventsChart').getContext('2d');
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: eventNames,
            datasets: [{
              label: 'Attendance Count',
              data: attendanceCounts,
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
            }]
          },
          options: {
            scales: {
              y: {
                beginAtZero: true,
                precision: 0
              }
            },
          }
        });
      })
      .catch(error => console.error('Error fetching top events data:', error));
  }

function capacity_utilization(){
    fetch('/capacity-utilization/')
    .then(response => response.json())
    .then(data => {
      const eventLabels = data.map(item => `${item.event_name} (${item.start_date})`);
      const venueCaps = data.map(item => item.venue_capacity);
      const registeredAttendees = data.map(item => item.registered_attendees);
      const attendedCounts = data.map(item => item.attended_count);

      const ctx = document.getElementById('capacityUtilizationChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: eventLabels,
          datasets: [
            {
              label: 'Venue Capacity',
              data: venueCaps,
              backgroundColor: 'hsl(7, 11%, 50%, 0.6)',
              borderColor: '#8e7673',
              borderWidth: 3
            },
            {
              label: 'Attended',
              data: attendedCounts,
              backgroundColor: 'hsl(4, 100%, 41%, 0.6)',
              borderColor: 'hsl(4, 100%, 41%)',
              borderWidth: 3
            }
          ]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              precision: 0
            }
          },
          plugins: {
            title: {
              display: true,
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
    })
    .catch(error => console.error('Error fetching capacity utilization data:', error));
}

function next_location(){
// Reference to the dropdown and chart container
const eventFilter = document.getElementById("event-filter");
const eventName = document.getElementById("event-name");
const ctx = document.getElementById("nextLocationChart").getContext("2d");
let chartInstance; // Store Chart.js instance for updates

// Function to fetch and update chart data
function updateChart(eventType) {
  const borderPalette = [
    '#FF0000',   // pure red
    '#E53935',   // deep red
    '#D32F2F',   // crimson red
    '#C62828',   // dark red
    '#B71C1C',   // maroon
    '#FF5252',   // coral red
    '#FF1744',   // bright red
    '#D50000',   // vivid red
    '#F44336',   // soft red
    '#E57373'    // light red
  ];
  
  const bgPalette = [
    'hsla(0, 100%, 50%, 0.6)',    // pure red
    'hsla(0, 78%, 45%, 0.6)',     // deep red
    'hsla(0, 67%, 40%, 0.6)',     // crimson red
    'hsla(0, 62%, 36%, 0.6)',     // dark red
    'hsla(0, 74%, 29%, 0.6)',     // maroon
    'hsla(0, 100%, 64%, 0.6)',    // coral red
    'hsla(0, 92%, 57%, 0.6)',     // bright red
    'hsla(0, 100%, 41%, 0.6)',    // vivid red
    'hsla(0, 86%, 60%, 0.6)',     // soft red
    'hsla(0, 100%, 70%, 0.6)'     // light red
  ];
    fetch(`/attendance_chart_data/${encodeURIComponent(eventType)}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error(data.error);
                return;
            }

            // Update the event name
            eventName.textContent = data.event_name;

            // Update the chart
            if (chartInstance) {
                chartInstance.destroy(); // Destroy the old chart before creating a new one
            }

            chartInstance = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.labels, // Locations
                    datasets: [{
                        label: "Attendance Count",
                        data: data.data, // Counts
                        backgroundColor: bgPalette, 
                        borderColor: borderPalette,
                        borderWidth: 3,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        })
        .catch(error => console.error("Error loading chart data:", error));
}

// Event listener for dropdown change
eventFilter.addEventListener("change", (e) => {
    updateChart(e.target.value);
});

// Initialize chart with the first event type
updateChart(eventFilter.value);
}

document.addEventListener('DOMContentLoaded', function(){
    attendance_day()
    capacity_utilization()
    getTop3Events()
    next_location()
})
