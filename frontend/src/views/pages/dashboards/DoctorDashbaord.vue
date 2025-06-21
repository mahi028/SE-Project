<script setup>
import AppointmentRequests from '@/components/doctorDashboard/AppointmentRequests.vue';
import DoctorNotificationsWidget from '@/components/doctorDashboard/DoctorNotificationsWidget.vue';
import DoctorAppointments from '@/components/doctorDashboard/DoctorAppointments.vue';
import DoctorSchedule from '@/components/doctorDashboard/DoctorSchedule.vue';
import QuickButtons from '@/components/QuickButtons.vue';
import Divider from 'primevue/divider';
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <QuickButtons page="doctor"/>

        <div class="col-span-12 xl:col-span-12">
            <Divider align="left" type="solid">
                <h3>Quick Widgets</h3>
            </Divider>
        </div>
        <div class="col-span-12 xl:col-span-6">
            <DoctorAppointments />
            <AppointmentRequests />
        </div>
        <div class="col-span-12 xl:col-span-6">
            <DoctorSchedule />
            <DoctorNotificationsWidget />
        </div>
    </div>
</template>
