<script setup>
import { seniorSchedules } from '@/service/SeniorScheduleSevice';
import { onMounted, ref } from 'vue';

const schedules = ref(null);

onMounted(() => {
    seniorSchedules.getScheuldes().then((data) => (schedules.value = data));
});
</script>

<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">Medicinal Schedules</div>
        <DataTable :value="schedules" :rows="5" :paginator="true" responsiveLayout="scroll">
            <Column field="label" header="Label" style="width: 30%"></Column>
            <Column field="date" header="Date" :sortable="true" style="width: 30%"></Column>
            <Column field="time" header="Time" style="width: 30%"></Column>
            <Column style="width: 15%" header="View">
                <template #body>
                    <RouterLink to="#"> <!-- :to="/sen/{{ ezId }}" -->
                        <Button icon="pi pi-search" type="button" class="p-button-text"></Button>
                    </RouterLink>
                </template>
            </Column>
        </DataTable>
    </div>
</template>
