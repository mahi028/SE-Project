import { userService } from './UserService.js';

export const appointmentService = {
    getAppointmentData() {
        return [
            // Doctor D001 appointments (4 total)
            {sen_id: 'S001', doc_id: 'D001', date: '2024-05-15', time: '09:00 AM', reason: 'Regular health checkup and blood pressure monitoring'},
            {sen_id: 'S003', doc_id: 'D001', date: '2024-05-16', time: '10:30 AM', reason: 'Chest pain and breathing difficulties'},
            {sen_id: 'S005', doc_id: 'D001', date: '2024-05-17', time: '02:00 PM', reason: 'Follow-up consultation for diabetes management'},
            {sen_id: 'S007', doc_id: 'D001', date: '2024-05-18', time: '11:00 AM', reason: 'Joint pain and mobility issues'},

            // Other doctors appointments
            {sen_id: 'S002', doc_id: 'D002', date: '2024-05-15', time: '11:00 AM', reason: 'Skin rash and allergic reactions'},
            {sen_id: 'S004', doc_id: 'D003', date: '2024-05-15', time: '03:30 PM', reason: 'Eye examination and vision problems'},
            {sen_id: 'S006', doc_id: 'D004', date: '2024-05-16', time: '09:30 AM', reason: 'Heart palpitations and chest discomfort'},
            {sen_id: 'S008', doc_id: 'D005', date: '2024-05-16', time: '01:00 PM', reason: 'Mental health consultation and anxiety'},
            {sen_id: 'S009', doc_id: 'D006', date: '2024-05-17', time: '10:00 AM', reason: 'Dermatological consultation for age spots'},
            {sen_id: 'S010', doc_id: 'D007', date: '2024-05-17', time: '04:00 PM', reason: 'Orthopedic consultation for back pain'},

            {sen_id: 'S001', doc_id: 'D008', date: '2024-05-18', time: '09:00 AM', reason: 'Neurological assessment for memory issues'},
            {sen_id: 'S002', doc_id: 'D009', date: '2024-05-18', time: '02:30 PM', reason: 'Gastroenterology consultation for digestive issues'},
            {sen_id: 'S003', doc_id: 'D010', date: '2024-05-19', time: '10:30 AM', reason: 'Pulmonology consultation for breathing problems'},
            {sen_id: 'S004', doc_id: 'D011', date: '2024-05-19', time: '03:00 PM', reason: 'Wellness checkup and preventive care'},
            {sen_id: 'S005', doc_id: 'D012', date: '2024-05-20', time: '11:30 AM', reason: 'Gynecological consultation'},

            {sen_id: 'S006', doc_id: 'D013', date: '2024-05-20', time: '01:30 PM', reason: 'General medicine consultation for fatigue'},
            {sen_id: 'S007', doc_id: 'D014', date: '2024-05-21', time: '09:30 AM', reason: 'Routine health screening'},
            {sen_id: 'S008', doc_id: 'D015', date: '2024-05-21', time: '02:00 PM', reason: 'Medication review and adjustment'},
            {sen_id: 'S009', doc_id: 'D016', date: '2024-05-22', time: '10:00 AM', reason: 'ENT consultation for hearing problems'},
            {sen_id: 'S010', doc_id: 'D017', date: '2024-05-22', time: '04:30 PM', reason: 'Care coordination and treatment planning'},

            {sen_id: 'S001', doc_id: 'D018', date: '2024-05-23', time: '11:00 AM', reason: 'Health assessment and lab results review'},
            {sen_id: 'S001', doc_id: 'D018', date: '2025-07-23', time: '11:00 AM', reason: 'Health assessment and lab results review'},
            {sen_id: 'S002', doc_id: 'D019', date: '2024-05-23', time: '03:30 PM', reason: 'Bone density consultation'},
            {sen_id: 'S003', doc_id: 'D020', date: '2024-05-24', time: '09:00 AM', reason: 'Pediatric consultation for grandchild'},
            {sen_id: 'S004', doc_id: 'D021', date: '2024-05-24', time: '01:00 PM', reason: 'Dermatology follow-up for skin condition'},
            {sen_id: 'S005', doc_id: 'D022', date: '2024-05-25', time: '10:30 AM', reason: 'Women\'s health consultation'},

            {sen_id: 'S006', doc_id: 'D023', date: '2024-05-25', time: '02:30 PM', reason: 'Mental health follow-up'},
            {sen_id: 'S007', doc_id: 'D024', date: '2024-05-26', time: '11:30 AM', reason: 'Ophthalmology consultation'},
            {sen_id: 'S008', doc_id: 'D025', date: '2024-05-26', time: '04:00 PM', reason: 'Medical consultation and health planning'},
            {sen_id: 'S009', doc_id: 'D026', date: '2024-05-27', time: '09:30 AM', reason: 'Specialist consultation'},
            {sen_id: 'S010', doc_id: 'D027', date: '2024-05-27', time: '01:30 PM', reason: 'Comprehensive health evaluation'},

            // Additional appointments for variety
            {sen_id: 'S002', doc_id: 'D028', date: '2024-05-28', time: '10:00 AM', reason: 'Clinical consultation and treatment review'},
            {sen_id: 'S004', doc_id: 'D029', date: '2024-05-28', time: '03:00 PM', reason: 'Family care consultation'},
            {sen_id: 'S006', doc_id: 'D030', date: '2024-05-29', time: '11:00 AM', reason: 'Regional health assessment'}
        ];
    },

    async getAppointmentsBySenior(seniorEzId) {
        const appointments = this.getAppointmentData().filter(appointment => appointment.sen_id === seniorEzId);

        // Enrich with doctor information
        const enrichedAppointments = await Promise.all(
            appointments.map(async (appointment) => {
                const doctor = await userService.getUser({ ez_id: appointment.doc_id });
                return {
                    ...appointment,
                    doctorEmail: doctor ? doctor.email : 'Unknown Doctor'
                };
            })
        );

        return enrichedAppointments;
    },

    async getAppointmentsByDoctor(doctorEzId) {
        const appointments = this.getAppointmentData().filter(appointment => appointment.doc_id === doctorEzId);

        // Enrich with senior information
        const enrichedAppointments = await Promise.all(
            appointments.map(async (appointment) => {
                const senior = await userService.getUser({ ez_id: appointment.sen_id });
                return {
                    ...appointment,
                    seniorEmail: senior ? senior.email : 'Unknown Senior'
                };
            })
        );

        return enrichedAppointments;
    },

    getAllAppointments() {
        return Promise.resolve(this.getAppointmentData());
    },

    getAppointmentsBetweenDoctorAndSenior(doctorEzId, seniorEzId) {
        const appointments = this.getAppointmentData().filter(appointment =>
            appointment.doc_id === doctorEzId && appointment.sen_id === seniorEzId
        );
        return Promise.resolve(appointments);
    },

    async getAvailableSlots(doctorEzId, selectedDate) {
        try {

            // Get existing appointments for this doctor on the selected date
            const existingAppointments = this.getAppointmentData().filter(appointment =>
                appointment.doc_id === doctorEzId && appointment.date === selectedDate
            );


            // Get doctor's available time slots
            const { doctorService } = await import('./DoctorService.js')
            const slots = await doctorService.getAvailableTimeSlots(doctorEzId, selectedDate)

            // Ensure slots is an array
            if (!Array.isArray(slots)) {
                return []
            }

            // Mark slots as unavailable if they conflict with existing appointments
            const availableSlots = slots.map(slot => ({
                ...slot,
                available: !existingAppointments.some(apt => apt.time === slot.time)
            }))

            return availableSlots

        } catch (error) {
            return []
        }
    },

    bookAppointment(appointmentData) {
        // Check if slot is still available
        const { doc_id, date, time } = appointmentData;
        const existingAppointment = this.getAppointmentData().find(apt =>
            apt.doc_id === doc_id && apt.date === date && apt.time === time
        );

        if (existingAppointment) {
            return Promise.reject(new Error('This time slot is no longer available'));
        }

        // Generate appointment ID
        const appointmentId = `APT_${Date.now()}`;

        // Create new appointment
        const newAppointment = {
            appointment_id: appointmentId,
            ...appointmentData,
            status: 'confirmed',
            created_at: new Date().toISOString()
        };

        // In a real app, this would save to database
        // For now, we'll simulate success
        return Promise.resolve(newAppointment);
    }
};
