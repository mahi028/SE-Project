<script setup>
import PeerGroups from '@/components/seniorDashboard/PeerGroups.vue';
import VitalLogs from '@/components/seniorDashboard/VitalLogs.vue';
import Contacts from '@/components/seniorDashboard/EmergencyContacts.vue';
import SeniorNotificationsWidget from '@/components/seniorDashboard/SeniorNotificationsWidget.vue';
import SeniorAppointments from '@/components/seniorDashboard/SeniorAppointments.vue';
import SeniorSchedule from '@/components/seniorDashboard/SeniorSchedule.vue';
import VitalTrend from '@/components/VitalTrend.vue';
import QuickButtons from '@/components/QuickButtons.vue';
import Divider from 'primevue/divider';
import { useLoginStore } from '@/store/loginStore';
import { ref } from 'vue';

const loginStore = useLoginStore()
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

    <!-- Responsive Widget Selector -->
    <div class="mb-6">
        <div class="card">
            <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <h4 class="text-lg font-semibold text-surface-700 dark:text-surface-300">Dashboard Widgets</h4>

                <!-- Mobile/Tablet: Dropdown -->
                <div class="lg:hidden w-full">
                    <Select
                        v-model="value"
                        :options="options"
                        optionLabel="name"
                        optionValue="value"
                        placeholder="Select a Widget"
                        class="w-full"
                    />
                </div>

                <!-- Desktop: Button Group -->
                <div class="hidden lg:block">
                    <SelectButton
                        v-model="value"
                        :options="options"
                        optionLabel="name"
                        optionValue="value"
                        class="responsive-select-button"
                    />
                </div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12 xl:col-span-6" v-show="value === '1'">
            <SeniorSchedule />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '1'">
            <SeniorAppointments />
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '2'">
            <VitalLogs :ezId="loginStore.ezId"/>
        </div>
        <div class="col-span-12 xl:col-span-6" v-show="value === '2'">
            <VitalTrend :ezId="loginStore.ezId"/>
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

<style scoped>
/* Responsive SelectButton styling */
:deep(.responsive-select-button .p-selectbutton) {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
}

:deep(.responsive-select-button .p-button) {
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    max-width: 160px;
}

/* Mobile responsiveness */
@media (max-width: 1024px) {
    :deep(.responsive-select-button .p-button) {
        font-size: 0.75rem;
        padding: 0.375rem 0.5rem;
        max-width: 120px;
    }
}

@media (max-width: 640px) {
    .grid {
        gap: 1rem;
    }
}
</style>
