<script setup>
import AppointmentRequests from '@/components/doctorDashboard/AppointmentRequests.vue';
import DoctorNotificationsWidget from '@/components/doctorDashboard/DoctorNotificationsWidget.vue';
import DoctorAppointments from '@/components/doctorDashboard/DoctorAppointments.vue';
import QuickButtons from '@/components/QuickButtons.vue';
import Divider from 'primevue/divider';
import { ref } from 'vue';

const value = ref('Appointments | Requests');
const options = ref(['Appointments | Requests', 'Notifications']);
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <QuickButtons page="mod"/>
    </div>
</template>
