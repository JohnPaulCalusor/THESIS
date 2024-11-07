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

function capacity_utilization(){
    fetch('/capacity-utilization/')
    .then(response => response.json())
    .then(data => {
      const eventNames = data.map(item => item.event_name);
      const venueCaps = data.map(item => item.venue_capacity);
      const registeredAttendees = data.map(item => item.registered_attendees);
      const attendedCounts = data.map(item => item.attended_count);

      const ctx = document.getElementById('capacityUtilizationChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: eventNames,
          datasets: [
            {
              label: 'Venue Capacity',
              data: venueCaps,
              backgroundColor: 'rgba(75, 192, 192, 0.2)',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
            },
            {
              label: 'Attended',
              data: attendedCounts,
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1
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
              text: 'Capacity Utilization'
            }
          },
          responsive: true,
          maintainAspectRatio: false
        }
      });
    })
    .catch(error => console.error('Error fetching capacity utilization data:', error));
}

document.addEventListener('DOMContentLoaded', function(){
    attendance_day()
    capacity_utilization()
})
