<script setup>
import { peerGroups } from '@/service/PeerGroupService';
import { onMounted, ref } from 'vue';

const groups = ref(null);
const pincode = ref('201011');

const reFetchGroups = ()=>{
    peerGroups.getPeerGroups(pincode.value).then((data) => (groups.value = data));
}

onMounted(() => {
    peerGroups.getPeerGroups(pincode.value).then((data) => (groups.value = data));
});
</script>

<template>
    <div class="card">
        <DataTable :value="groups" :rows="5" :paginator="true" responsiveLayout="scroll">
            <template #header>
                <div class="flex flex-wrap items-center justify-between gap-2">
                    <span class="text-xl font-bold">Vital Logs</span>
                    <div class="flex gap-2">
                        <Button severity="success" label="Log Vital" variant="text"/>
                    </div>
                </div>
            </template>
            <Column field="label" header="Label" style="width: 22.5%"></Column>
            <Column field="date" header="Date" style="width: 22.5%"></Column>
            <Column field="time" header="Time" style="width: 22.5%"></Column>
            <Column field="location" header="Location" style="width: 22.5%"></Column>
            <Column style="width: 10%" header="View">
                <template #body>
                    <Button icon="pi pi-search" type="button" class="p-button-text"></Button>
                </template>
            </Column>
        </DataTable>
    </div>
</template>
