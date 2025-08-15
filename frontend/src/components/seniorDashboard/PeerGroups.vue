<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useQuery, useMutation } from '@vue/apollo-composable';
import { useLoginStore } from '@/store/loginStore';
import gql from 'graphql-tag';

const toast = useToast();
const loginStore = useLoginStore();

const pincode = ref(loginStore.pincode || '201011');
const visible = ref(false);
const submitting = ref(false);
const showMyGroupsOnly = ref(false);

const newGroup = ref({
    label: '',
    day: '',
    time: null,
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

// GraphQL queries and mutations
const GET_GROUPS = gql`
    query GetGroups($pincode: String, $adminId: Int) {
        getGroups(pincode: $pincode, adminId: $adminId) {
            grpId
            label
            timing
            admin
            pincode
            location
            adminSen {
                senId
                ezId
                user {
                    name
                }
            }
        }
    }
`;

const CREATE_GROUP = gql`
    mutation CreateGroup($label: String!, $timing: DateTime!, $pincode: String, $location: String) {
        createGroup(label: $label, timing: $timing, pincode: $pincode, location: $location) {
            message
            status
        }
    }
`;

const JOIN_GROUP = gql`
    mutation JoinGroup($grpId: Int!) {
        joinGroup(grpId: $grpId) {
            message
            status
        }
    }
`;

// Determine query variables based on filter
const queryVariables = computed(() => {
    if (showMyGroupsOnly.value && loginStore.senInfo?.senId) {
        return { adminId: loginStore.senInfo.senId };
    }
    return { pincode: pincode.value || null };
});

// Apollo composables
const { result, loading, error, refetch } = useQuery(GET_GROUPS, queryVariables, {
    fetchPolicy: 'cache-and-network'
});
const { mutate: createGroup } = useMutation(CREATE_GROUP);
const { mutate: joinGroup } = useMutation(JOIN_GROUP);

// Process groups data
const groups = computed(() => {
    const rawGroups = result.value?.getGroups || [];
    return rawGroups.map(group => {
        const groupDate = new Date(group.timing);
        return {
            grpId: group.grpId,
            label: group.label,
            day: getDayFromDate(groupDate),
            time: formatTime(groupDate),
            location: group.location || 'Location TBD',
            adminName: group.adminSen?.user?.name || 'Unknown',
            isMyGroup: group.admin === loginStore.senInfo?.senId,
            timing: group.timing,
            admin: group.admin,
            pincode: group.pincode
        };
    });
});

// Helper functions
const getDayFromDate = (date) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.getDay()];
};

const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const openCreateGroup = () => {
    newGroup.value = {
        label: '',
        day: '',
        time: null,
        location: ''
    };
    visible.value = true;
};

const cancelGroup = () => {
    visible.value = false;
    newGroup.value = {
        label: '',
        day: '',
        time: null,
        location: ''
    };
};

const submitGroup = async () => {
    if (!isFormValid()) {
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
        // Create a proper datetime from day and time
        const groupDateTime = createDateTimeFromDayAndTime(newGroup.value.day, newGroup.value.time);

        const { data } = await createGroup({
            label: newGroup.value.label,
            timing: groupDateTime.toISOString(),
            pincode: pincode.value || null,
            location: newGroup.value.location
        });

        const response = data?.createGroup;

        if (response?.status === 1) {
            toast.add({
                severity: 'success',
                summary: 'Group Created',
                detail: response.message || `"${newGroup.value.label}" peer group has been created successfully!`,
                life: 3000
            });

            // Refetch groups to update the list
            await refetch();
            cancelGroup();
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to create group. Please try again.',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error creating group:', error);
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

const handleJoinGroup = async (group) => {
    try {
        const { data } = await joinGroup({
            grpId: group.grpId
        });

        const response = data?.joinGroup;

        if (response?.status === 1) {
            toast.add({
                severity: 'success',
                summary: 'Joined Group',
                detail: response.message || `You have joined "${group.label}" successfully!`,
                life: 3000
            });

            // Refetch groups to update the list
            await refetch();
        } else if (response?.status === 0) {
            toast.add({
                severity: 'info',
                summary: 'Already Joined',
                detail: response.message || `You are already a member of "${group.label}".`,
                life: 3000
            });
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to join group. Please try again.',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error joining group:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to join group. Please try again.',
            life: 3000
        });
    }
};

const createDateTimeFromDayAndTime = (day, timeDate) => {
    if (!timeDate || !day) return new Date();

    const now = new Date();
    const targetDate = new Date(now);

    // Set the time from the Calendar time picker
    const hours = timeDate.getHours();
    const minutes = timeDate.getMinutes();

    // Calculate target day
    const currentDay = now.getDay();
    const targetDay = getDayIndex(day);

    let daysToAdd = targetDay - currentDay;
    if (daysToAdd <= 0) {
        daysToAdd += 7; // Next week
    }

    targetDate.setDate(now.getDate() + daysToAdd);
    targetDate.setHours(hours, minutes, 0, 0);

    return targetDate;
};

const getDayIndex = (dayName) => {
    const days = {
        'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
        'Thursday': 4, 'Friday': 5, 'Saturday': 6,
        'Daily': 1, 'Weekdays': 1, 'Weekends': 0
    };
    return days[dayName] || 1;
};

const isFormValid = () => {
    return newGroup.value.label.trim() &&
           newGroup.value.day &&
           newGroup.value.time &&
           newGroup.value.location.trim();
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

const reFetchGroups = async () => {
    try {
        await refetch(queryVariables.value);
    } catch (error) {
        console.error('Error refetching groups:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to refresh groups',
            life: 3000
        });
    }
};

const toggleGroupFilter = () => {
    showMyGroupsOnly.value = !showMyGroupsOnly.value;
};

onMounted(() => {
    // Data is automatically fetched by useQuery
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
                <!-- Loading state -->
                <div v-if="loading" class="text-center py-8">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                    <p class="mt-4">Loading groups...</p>
                </div>

                <!-- Error state -->
                <div v-else-if="error" class="text-center py-8">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                    <p class="text-red-600">Failed to load peer groups</p>
                    <Button label="Retry" @click="reFetchGroups" class="mt-3" />
                </div>

                <!-- Content -->
                <div v-else>
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
                            <ToggleButton
                                v-model="showMyGroupsOnly"
                                onLabel="My Groups"
                                offLabel="All Groups"
                                onIcon="pi pi-user"
                                offIcon="pi pi-users"
                                @click="toggleGroupFilter"
                                class="flex-shrink-0"
                            />
                            <div class="flex gap-2 items-end" v-if="!showMyGroupsOnly">
                                <div class="flex flex-col">
                                    <label for="pincode" class="text-sm font-medium text-gray-700 mb-1">Pincode</label>
                                    <InputText
                                        id="pincode"
                                        v-model="pincode"
                                        placeholder="Enter pincode"
                                        class="w-full"
                                        style="min-width: 120px;"
                                    />
                                </div>
                                <Button
                                    icon="pi pi-search"
                                    outlined
                                    @click="reFetchGroups"
                                    v-tooltip.top="'Search groups in this pincode'"
                                    class="flex-shrink-0"
                                    style="height: 42px;"
                                />
                            </div>
                        </div>
                    </div>

                    <!-- Active Filters Display -->
                    <div v-if="showMyGroupsOnly || pincode" class="flex flex-wrap gap-2 items-center mb-4">
                        <span class="text-sm text-gray-600">Active filters:</span>
                        <Chip v-if="showMyGroupsOnly" label="My Groups Only" removable @remove="showMyGroupsOnly = false" />
                        <Chip v-if="!showMyGroupsOnly && pincode" :label="`Pincode: ${pincode}`" removable @remove="() => { pincode = ''; reFetchGroups(); }" />
                    </div>

                    <!-- Results Count -->
                    <div class="text-sm text-gray-600 mb-4">
                        Showing {{ groups.length }} group(s)
                    </div>

                    <DataTable
                        v-if="groups && groups.length"
                        :value="groups"
                        :rows="8"
                        :paginator="true"
                        responsiveLayout="scroll"
                        class="peer-groups-table"
                    >
                        <Column field="label" header="Group Name" style="min-width: 200px">
                            <template #body="{ data }">
                                <div class="flex items-center gap-3">
                                    <Avatar
                                        :label="data.label.charAt(0)"
                                        class="bg-green-500 text-white"
                                        shape="circle"
                                        size="normal"
                                    />
                                    <div>
                                        <div class="font-medium text-surface-900 dark:text-surface-0">{{ data.label }}</div>
                                        <div class="text-xs text-surface-500 dark:text-surface-400">
                                            Admin: {{ data.adminName }}
                                        </div>
                                    </div>
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
                                    <span class="text-surface-700 dark:text-surface-300 text-sm">{{ data.location }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column header="Actions" style="width: 120px">
                            <template #body="{ data }">
                                <div v-if="data.isMyGroup" class="flex items-center gap-2">
                                    <Tag value="My Group" severity="success" class="text-xs" />
                                </div>
                                <Button
                                    v-else
                                    label="Join"
                                    icon="pi pi-user-plus"
                                    size="small"
                                    severity="info"
                                    @click="handleJoinGroup(data)"
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
                                {{ showMyGroupsOnly ? 'No Groups Created Yet' : 'No Peer Groups Found' }}
                            </h4>
                            <p class="text-surface-500 dark:text-surface-400 mb-4">
                                {{ showMyGroupsOnly
                                    ? 'You haven\'t created any peer groups yet. Start by creating your first group!'
                                    : 'Create the first peer group in your area or try a different pincode.' }}
                            </p>
                            <Button
                                :label="showMyGroupsOnly ? 'Create Your First Group' : 'Create New Group'"
                                icon="pi pi-plus"
                                severity="success"
                                @click="openCreateGroup"
                            />
                        </div>
                    </div>
                </div>
            </template>
        </Card>

        <!-- Enhanced Create Group Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            header="Create Peer Group"
            :style="{ width: '600px' }"
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
                        <label for="groupLabel" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Group Name *</label>
                        <InputText
                            id="groupLabel"
                            v-model="newGroup.label"
                            placeholder="e.g., Morning Walking Group"
                            class="w-full"
                        />
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pr-md-2">
                        <label for="groupDay" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Meeting Day *</label>
                        <Select
                            id="groupDay"
                            v-model="newGroup.day"
                            :options="weekdays"
                            optionLabel="label"
                            optionValue="value"
                            placeholder="Select meeting day"
                            class="w-full"
                        />
                    </div>

                    <div class="field col-12 md:col-6 mb-4 pl-md-2">
                        <label for="groupTime" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Meeting Time *</label>
                        <Calendar
                            id="groupTime"
                            v-model="newGroup.time"
                            timeOnly
                            hourFormat="12"
                            showIcon
                            placeholder="Select time"
                            class="w-full"
                        />
                        <small class="text-surface-500 dark:text-surface-400 mt-1 block">
                            Select the meeting time using the time picker
                        </small>
                    </div>

                    <div class="field col-12 mb-4">
                        <label for="groupLocation" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">Meeting Location *</label>
                        <Textarea
                            id="groupLocation"
                            v-model="newGroup.location"
                            placeholder="e.g., Central Park, Main Gate"
                            class="w-full"
                            rows="2"
                        />
                    </div>
                </div>

                <div class="info-section">
                    <div class="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-green-500 mt-1"></i>
                        <div class="text-sm text-green-700 dark:text-green-300">
                            <p class="font-medium mb-2">EZCare Peer Group Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Choose a convenient time and location for regular meetings</li>
                                <li>• Select activities that interest your target group</li>
                                <li>• Ensure the location is accessible for seniors</li>
                                <li>• Groups are visible to others in your pincode area through EZCare</li>
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
                        :disabled="!isFormValid()"
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
    .flex.flex-col.sm\:flex-row {
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
