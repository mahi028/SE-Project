export const notificationService = {
    getNotificationData(){
        return {
                today: [
                    {type: 'Appointment', name: 'Mr. Mishra', time: '5:00 PM', time_left:'1 Hour'},
                    {type: 'Appointment', name: 'Mr. Chopra', time: '5:30 PM', time_left:'1 Hour 30 Min'},
                    {type: 'Vital', name: 'Mr. Chopra', label: 'Blood Pressure', serverity: 'low'},
                ],
                yesterday: [
                    {type: 'Appointment', name: 'Mr. Mishra', time: '5:00 PM', time_left:'1 day'},
                    {type: 'Appointment', name: 'Mr. Chopra', time: '5:30 PM', time_left:'1 day'},
                ]
            }
    },
    getNotifications() {
        return Promise.resolve(this.getNotificationData());
    },
}
