<script setup>
import PeerGroups from '@/components/seniorDashboard/PeerGroups.vue';
import VitalLogs from '@/components/seniorDashboard/VitalLogs.vue';
import Contacts from '@/components/seniorDashboard/EmergencyContacts.vue';
import SeniorNotificationsWidget from '@/components/seniorDashboard/SeniorNotificationsWidget.vue';
import SeniorAppointments from '@/components/seniorDashboard/SeniorAppointments.vue';
import SeniorSchedule from '@/components/seniorDashboard/SeniorSchedule.vue';
import QuickButtons from '@/components/QuickButtons.vue';
import Divider from 'primevue/divider';
import { ref } from 'vue';

const value = ref('1');
const options = ref([
        {name: 'Appointments and Schedules', value: '1'},
        {name: 'Vitals', value: '2'},
        {name: 'Contacts', value: '3'},
        {name: 'Groups', value: '4'},
        {name: 'Notifications', value: '5'}
    ]
);
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <QuickButtons page="senior"/>

        <div class="col-span-12 xl:col-span-12">
            <Divider align="left" type="solid">
                <h3>Quick Widgets</h3>
            </Divider>
        </div>
    </div>
    <div>
        <SelectButton v-model="value" :options="options" optionLabel="name" optionValue="value" />
        <!-- <Select v-model="value" :options="options" optionLabel="name" optionValue="value" placeholder="Select a Widget" class="w-full md:w-56" /> -->
    </div>
    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12 xl:col-span-6" v-show="value === '1'">
            <SeniorSchedule />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '1'">
            <SeniorAppointments />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '2'">
            <VitalLogs />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '3'">
            <Contacts/>
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '4'">
            <PeerGroups />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '5'">
            <SeniorNotificationsWidget />
        </div>
    </div>
</template>
