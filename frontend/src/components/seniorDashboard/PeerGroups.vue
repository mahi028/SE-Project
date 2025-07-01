<script setup>
import { peerGroups } from '@/service/PeerGroupService';
import { onMounted, ref } from 'vue';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const groups = ref(null);
const pincode = ref('201011');
const visible = ref(false);

const newGroup = ref({
    label: '',
    date: '',
    time: '',
    location: ''
});

const openCreateGroup = () => {
    visible.value = true;
};

const submitGroup = () => {
    if (!newGroup.value.label || !newGroup.value.date || !newGroup.value.time || !newGroup.value.location) {
        toast.add({ severity: 'warn', summary: 'Missing Info', detail: 'Please fill all fields.', life: 3000 });
        return;
    }

    // Optional: call an API to save it, here we just push locally
    groups.value.push({ ...newGroup.value });

    toast.add({ severity: 'success', summary: 'Success', detail: 'Peer Group Created.', life: 3000 });

    visible.value = false;
    newGroup.value = { label: '', date: '', time: '', location: '' };
};

const reFetchGroups = () => {
    peerGroups.getPeerGroups(pincode.value).then((data) => (groups.value = data));
};

onMounted(() => {
    peerGroups.getPeerGroups(pincode.value).then((data) => (groups.value = data));
});
</script>

<template>
    <Toast />
    <div class="card">
        <DataTable :value="groups" :rows="5" :paginator="true" responsiveLayout="scroll">
            <template #header>
                <div class="flex flex-wrap items-center justify-between gap-2">
                    <span class="text-xl font-bold">Peer Groups</span>
                    <div class="flex gap-2">
                        <Button severity="success" label="Create Group" variant="text" @click="openCreateGroup" />
                        <FloatLabel>
                            <InputText id="over_label" v-model="pincode" />
                            <label for="over_label">Pincode</label>
                        </FloatLabel>
                        <Button icon="pi pi-refresh" rounded raised @click="reFetchGroups" />
                    </div>
                </div>
            </template>
            <Column field="label" header="Label" style="width: 22.5%" />
            <Column field="date" header="Date" style="width: 22.5%" />
            <Column field="time" header="Time" style="width: 22.5%" />
            <Column field="location" header="Location" style="width: 22.5%" />
            <Column style="width: 10%" header="View">
                <template #body>
                    <Button icon="pi pi-search" type="button" class="p-button-text" />
                </template>
            </Column>
        </DataTable>

        <!-- Overlay Dialog -->
        <Dialog v-model:visible="visible" modal header="Create Peer Group" :style="{ width: '30rem' }">
            <div class="flex flex-col gap-4">
                <label for="label" class="text-sm font-medium text-gray-700">Label</label>
                <InputText id="label" v-model="newGroup.label" class="w-full" />

                <label for="date" class="text-sm font-medium text-gray-700">Date</label>
                <InputText id="date" v-model="newGroup.date" class="w-full" placeholder="e.g. Sunday, Everyday" />

                <label for="time" class="text-sm font-medium text-gray-700">Time</label>
                <InputText id="time" v-model="newGroup.time" class="w-full" placeholder="e.g. 7:00 AM" />

                <label for="location" class="text-sm font-medium text-gray-700">Location</label>
                <InputText id="location" v-model="newGroup.location" class="w-full" />

                <div class="flex justify-end mt-4">
                    <Button label="Submit" icon="pi pi-check" class="bg-green-500 text-white" @click="submitGroup" />
                </div>
            </div>
        </Dialog>
    </div>
</template>
