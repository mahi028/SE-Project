<script setup>
import { peerGroups } from '@/service/PeerGroupService';
import { onMounted, ref } from 'vue';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const groups = ref(null);
const pincode = ref('201011');
const visible = ref(false);
const submitting = ref(false);

const newGroup = ref({
    label: '',
    day: '',
    time: '',
    location: ''
});

const weekdays = [
    { label: 'Monday', value: 'Monday' },
    { label: 'Tuesday', value: 'Tuesday' },
    { label: 'Wednesday', value: 'Wednesday' },
    { label: 'Thursday', value: 'Thursday' },
    { label: 'Friday', value: 'Friday' },
    { label: 'Saturday', value: 'Saturday' },
    { label: 'Sunday', value: 'Sunday' },
    { label: 'Daily', value: 'Daily' },
    { label: 'Weekdays', value: 'Weekdays' },
    { label: 'Weekends', value: 'Weekends' }
];

const openCreateGroup = () => {
    newGroup.value = { label: '', day: '', time: '', location: '' };
    visible.value = true;
};

const cancelGroup = () => {
    visible.value = false;
    newGroup.value = { label: '', day: '', time: '', location: '' };
};

const submitGroup = async () => {
    if (!newGroup.value.label || !newGroup.value.day || !newGroup.value.time || !newGroup.value.location) {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields.',
            life: 3000
        });
        return;
    }

    submitting.value = true;
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));

        groups.value.push({ ...newGroup.value });

        toast.add({
            severity: 'success',
            summary: 'Group Created',
            detail: `"${newGroup.value.label}" peer group has been created successfully!`,
            life: 3000
        });

        cancelGroup();
    } catch (error) {
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to create group. Please try again.',
            life: 3000
        });
    } finally {
        submitting.value = false;
    }
};

const joinGroup = (group) => {
    toast.add({
        severity: 'info',
        summary: 'Joined Group',
        detail: `You have joined "${group.label}"`,
        life: 3000
    });
};

const getDayColor = (day) => {
    switch (day.toLowerCase()) {
        case 'monday':
        case 'tuesday':
        case 'wednesday':
        case 'thursday':
        case 'friday':
        case 'weekdays':
            return 'info';
        case 'saturday':
        case 'sunday':
        case 'weekends':
            return 'warning';
        case 'daily':
            return 'success';
        default:
            return 'secondary';
    }
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
    <div class="peer-groups-card">
        <Card class="w-full">
            <template #header>
                <div class="section-header">
                    <i class="pi pi-users text-green-500"></i>
                    <h3 class="section-title">Peer Groups</h3>
                </div>
            </template>
            <template #content>
                <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                    <p class="text-surface-600 dark:text-surface-400">
                        Connect with like-minded seniors in your area through various group activities.
                    </p>
                    <div class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-end">
                        <Button
                            label="Create Group"
                            icon="pi pi-plus"
                            severity="success"
                            outlined
                            @click="openCreateGroup"
                            class="flex-shrink-0"
                        />
                        <div class="flex gap-2 items-end">
                            <FloatLabel class="flex-grow">
                                <InputText
                                    id="pincode"
                                    v-model="pincode"
                                    class="w-full"
                                    style="min-width: 120px;"
                                />
                                <label for="pincode">Pincode</label>
                            </FloatLabel>
                            <Button
                                icon="pi pi-refresh"
                                outlined
                                @click="reFetchGroups"
                                v-tooltip.top="'Refresh groups'"
                                class="flex-shrink-0"
                                style="height: 42px;"
                            />
                        </div>
                    </div>
                </div>

                <DataTable
                    v-if="groups && groups.length"
                    :value="groups"
                    :rows="5"
                    :paginator="true"
                    responsiveLayout="scroll"
                    class="peer-groups-table"
                >
                    <Column field="label" header="Group Name" style="min-width: 200px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <Avatar
                                    :label="data.label.charAt(0)"
                                    class="bg-green-500 text-white"
                                    shape="circle"
                                    size="small"
                                />
                                <span class="font-medium text-surface-900 dark:text-surface-0">{{ data.label }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="day" header="Schedule" style="min-width: 120px">
                        <template #body="{ data }">
                            <Tag
                                :value="data.day"
                                :severity="getDayColor(data.day)"
                                class="text-sm"
                            />
                        </template>
                    </Column>
                    <Column field="time" header="Time" style="min-width: 100px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <i class="pi pi-clock text-blue-500"></i>
                                <span class="text-surface-700 dark:text-surface-300">{{ data.time }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="location" header="Location" style="min-width: 150px">
                        <template #body="{ data }">
                            <div class="flex items-center gap-2">
                                <i class="pi pi-map-marker text-red-500"></i>
                                <span class="text-surface-700 dark:text-surface-300">{{ data.location }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column header="Actions" style="width: 120px">
                        <template #body="{ data }">
                            <Button
                                label="Join"
                                icon="pi pi-user-plus"
                                size="small"
                                severity="info"
                                @click="joinGroup(data)"
                                class="w-full"
                            />
                        </template>
                    </Column>
                </DataTable>

                <div v-else class="empty-state">
                    <div class="text-center py-12">
                        <div class="text-surface-400 dark:text-surface-500 mb-4">
                            <i class="pi pi-users text-6xl"></i>
                        </div>
                        <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                            No Peer Groups Found
                        </h4>
                        <p class="text-surface-500 dark:text-surface-400 mb-4">
                            Create the first peer group in your area or try a different pincode.
                        </p>
                        <Button
                            label="Create Your First Group"
                            icon="pi pi-plus"
                            severity="success"
                            @click="openCreateGroup"
                        />
                    </div>
                </div>
            </template>
        </Card>

        <!-- Enhanced Create Group Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            header="Create Peer Group"
            :style="{ width: '500px' }"
            :closable="!submitting"
            :dismissableMask="!submitting"
            class="peer-group-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i class="pi pi-users text-green-500 mr-2"></i>
                    <span>Create Peer Group</span>
                </div>
            </template>

            <div class="dialog-content">
                <div class="grid formgrid p-fluid">
                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <InputText
                                id="groupLabel"
                                v-model="newGroup.label"
                                class="w-full"
                            />
                            <label for="groupLabel">Group Name *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pr-md-2">
                        <FloatLabel>
                            <Select
                                id="groupDay"
                                v-model="newGroup.day"
                                :options="weekdays"
                                optionLabel="label"
                                optionValue="value"
                                class="w-full"
                            />
                            <label for="groupDay">Meeting Day *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pl-md-2">
                        <FloatLabel>
                            <InputText
                                id="groupTime"
                                v-model="newGroup.time"
                                class="w-full"
                            />
                            <label for="groupTime">Meeting Time *</label>
                        </FloatLabel>
                        <small class="text-surface-500 dark:text-surface-400 mt-1 block">
                            e.g., 7:00 AM
                        </small>
                    </div>

                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <Textarea
                                id="groupLocation"
                                v-model="newGroup.location"
                                class="w-full"
                                rows="2"
                            />
                            <label for="groupLocation">Meeting Location *</label>
                        </FloatLabel>
                    </div>
                </div>

                <div class="info-section">
                    <div class="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-green-500 mt-1"></i>
                        <div class="text-sm text-green-700 dark:text-green-300">
                            <p class="font-medium mb-1">Peer Group Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Choose a convenient time and location for regular meetings</li>
                                <li>• Select activities that interest your target group</li>
                                <li>• Ensure the location is accessible for seniors</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-4">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        @click="cancelGroup"
                        :disabled="submitting"
                        class="flex-shrink-0"
                    />
                    <Button
                        label="Create Group"
                        icon="pi pi-check"
                        severity="success"
                        @click="submitGroup"
                        :loading="submitting"
                        class="flex-shrink-0"
                    />
                </div>
            </template>
        </Dialog>
    </div>
</template>

<style scoped>
.peer-groups-card {
    max-width: 100%;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem 1.5rem 0;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 0;
}

.peer-groups-table {
    border-radius: 8px;
    overflow: hidden;
}

.empty-state {
    background: var(--surface-ground);
    border-radius: 12px;
    border: 2px dashed var(--surface-border);
}

.dialog-header {
    display: flex;
    align-items: center;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
}

.dialog-content {
    padding: 1.5rem 0;
}

.info-section {
    margin-top: 2rem;
}

/* Enhanced spacing for form fields */
.field.mb-4 {
    margin-bottom: 1.5rem !important;
}

.pr-md-2 {
    padding-right: 0.5rem;
}

.pl-md-2 {
    padding-left: 0.5rem;
}

/* Dark mode enhancements */
:global(.p-dark) .peer-groups-card :deep(.p-card) {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
}

:global(.p-dark) .dialog-header {
    color: var(--text-color);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .section-header {
        padding: 1rem 1rem 0;
    }

    .pr-md-2,
    .pl-md-2 {
        padding-left: 0;
        padding-right: 0;
    }

    .field.mb-4 {
        margin-bottom: 1.25rem !important;
    }

    .dialog-content {
        padding: 1rem 0;
    }
}

@media (max-width: 640px) {
    .flex.flex-col.sm\\:flex-row {
        align-items: stretch;
    }

    .flex.gap-2.items-end {
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
    }
}

/* Animation enhancements */
.peer-groups-table :deep(tr) {
    transition: all 0.3s ease;
}

.peer-groups-table :deep(tr:hover) {
    background: var(--surface-hover);
}

:deep(.p-button) {
    transition: all 0.3s ease;
}

:deep(.p-button:hover) {
    transform: translateY(-1px);
}
</style>
