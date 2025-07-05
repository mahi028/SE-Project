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

        <!-- <div class="col-span-12 xl:col-span-12">
            <Divider align="left" type="solid">
                <h3>Quick Widgets</h3>
            </Divider>
        </div> -->
    </div>
    <!-- <div>
        <SelectButton v-model="value" :options="options" optionLabel="name" optionValue="value" />
        <Select v-model="value" :options="options" optionLabel="name" optionValue="value" placeholder="Select a Widget" class="w-full md:w-56" />
    </div>
    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12 xl:col-span-6"  v-show="value==='Appointments | Requests'">
            <DoctorAppointments />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value==='Appointments | Requests'">
            <AppointmentRequests />
        </div>
    </div> -->
</template>
