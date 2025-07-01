export const notificationService = {
    getNotificationData(){
        return {
                today: [
                    {type: 'Appointment', name: 'Mr. Mishra', time: '5:00 PM', time_left:'1 Hour'},
                    {type: 'Appointment', name: 'Mr. Chopra', time: '5:30 PM', time_left:'1 Hour 30 Min'},
                    {type: 'Vital', name: 'Mr. Chopra', label: 'Blood Pressure', serverity: 'low'},

                    { type: 'Reminder', label: 'Drink Water', time: '4:00 PM' },
                    { type: 'Reminder', label: 'Walk Time', time: '6:00 AM' },
                    { type: 'Reminder', label: 'Take Medicine', time: '9:00 AM' }
                ],
                yesterday: [
                    {type: 'Appointment', name: 'Mr. Mishra', time: '5:00 PM', time_left:'1 day'},
                    {type: 'Appointment', name: 'Mr. Chopra', time: '5:30 PM', time_left:'1 day'},

                    { type: 'Reminder', label: 'Drink Water', time: '4:00 PM' },
                    { type: 'Reminder', label: 'Evening Walk', time: '6:30 PM' }
                ]
            }
    },
    getNotifications() {
        return Promise.resolve(this.getNotificationData());
    },
}