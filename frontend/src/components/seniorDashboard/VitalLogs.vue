<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useQuery, useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';

const toast = useToast();
const props = defineProps({
    ezId: String,
});

const visible = ref(false);
const submitting = ref(false);

const vitalForm = ref({
    selectedType: null,
    reading: ''
});

// GraphQL queries and mutations
const GET_VITAL_TYPES = gql`
    query GetVitalTypes {
        getVitalTypes {
            typeId
            label
            unit
            threshold
        }
    }
`;

const GET_VITAL_LOGS = gql`
    query GetVitalLogsBySenior {
        getVitalLogsBySenior {
            logId
            senId
            vitalTypeId
            reading
            loggedAt
            vitalType {
                typeId
                label
                unit
                threshold
            }
        }
    }
`;

const ADD_VITAL_LOG = gql`
    mutation AddVitalLog($vitalTypeId: Int!, $reading: String!, $loggedAt: DateTime) {
        addVitalLog(vitalTypeId: $vitalTypeId, reading: $reading, loggedAt: $loggedAt) {
            message
            status
        }
    }
`;

// Apollo composables with proper destructuring
const { result: vitalTypesResult, loading: loadingTypes, error: typesError } = useQuery(GET_VITAL_TYPES);
const { result: vitalLogsResult, loading: loadingLogs, error, refetch } = useQuery(GET_VITAL_LOGS);
const { mutate: addVitalLog } = useMutation(ADD_VITAL_LOG);

// Computed properties
const vitalTypes = computed(() => {
    const types = vitalTypesResult.value?.getVitalTypes || [];
    return types.map(type => ({
        label: type.label,
        value: type.typeId,
        unit: type.unit,
        placeholder: getPlaceholderForVitalType(type.label),
        thresholds: parseThreshold(type.threshold)
    }));
});

const selectedVitalType = computed(() => {
    return vitalTypes.value.find(type => type.value === vitalForm.value.selectedType?.value);
});

// Helper function to parse threshold JSON string
const parseThreshold = (thresholdString) => {
    if (!thresholdString) return null;
    try {
        return JSON.parse(thresholdString);
    } catch (error) {
        console.error('Error parsing threshold:', error);
        return null;
    }
};

// Create a map for quick vital type lookups
const vitalTypeMap = computed(() => {
    const types = vitalTypesResult.value?.getVitalTypes || [];
    const map = {};
    types.forEach(type => {
        map[type.typeId] = {
            label: type.label,
            unit: type.unit,
            threshold: parseThreshold(type.threshold)
        };
    });
    return map;
});

const vitals = computed(() => {
    const logs = vitalLogsResult.value?.getVitalLogsBySenior || [];
    return logs.map(log => {
        // Get vital type data - prioritize the relation data from GraphQL
        let vitalTypeData;

        if (log.vitalType) {
            // Use the related vitalType data from GraphQL
            vitalTypeData = {
                label: log.vitalType.label,
                unit: log.vitalType.unit,
                threshold: parseThreshold(log.vitalType.threshold)
            };
        } else {
            // Fallback to vitalTypeMap if relation is not loaded
            vitalTypeData = vitalTypeMap.value[log.vitalTypeId] || {
                label: 'Unknown',
                unit: '',
                threshold: null
            };
        }

        // Debug logging to see what data we're working with
        console.log('Processing vital log:', {
            logId: log.logId,
            reading: log.reading,
            vitalTypeLabel: vitalTypeData.label,
            threshold: vitalTypeData.threshold,
            vitalTypeId: log.vitalTypeId
        });

        const statusInfo = evaluateVitalStatus(
            vitalTypeData.label,
            log.reading,
            vitalTypeData.threshold
        );

        console.log('Status evaluation result:', statusInfo);

        return {
            id: log.logId,
            label: vitalTypeData.label,
            reading: log.reading,
            unit: vitalTypeData.unit,
            date: new Date(log.loggedAt).toLocaleDateString(),
            time: new Date(log.loggedAt).toLocaleTimeString(),
            statusInfo: statusInfo
        };
    });
});

// Helper functions
const getPlaceholderForVitalType = (label) => {
    switch (label.toLowerCase()) {
        case 'blood pressure':
            return '120/80';
        case 'heart rate':
            return '72';
        case 'body temperature':
            return '98.6';
        case 'blood sugar':
            return '100';
        case 'weight':
            return '70';
        case 'oxygen saturation':
            return '98';
        default:
            return 'Enter reading';
    }
};

const evaluateVitalStatus = (vitalType, reading, thresholds) => {
    console.log('Evaluating vital status:', { vitalType, reading, thresholds });

    if (!thresholds) {
        console.log('No thresholds found, returning irrelevant');
        return { status: 'irrelevant' };
    }

    // Special handling for blood pressure
    if (vitalType.toLowerCase() === 'blood pressure') {
        const match = reading.match(/(\d+)\/(\d+)/);
        if (!match) {
            console.log('Invalid blood pressure format');
            return { status: 'invalid' };
        }

        const systolic = parseInt(match[1]);
        const diastolic = parseInt(match[2]);

        console.log('Blood pressure values:', { systolic, diastolic, thresholds });

        if (thresholds.systolic && thresholds.diastolic) {
            // Check for low blood pressure first
            if (systolic < thresholds.systolic.low || diastolic < thresholds.diastolic.low) {
                console.log('Blood pressure is low');
                return { status: 'Low' };
            }
            // Check for high blood pressure
            if (systolic > thresholds.systolic.high || diastolic > thresholds.diastolic.high) {
                console.log('Blood pressure is high');
                return { status: 'High' };
            }
            // Normal range
            console.log('Blood pressure is normal');
            return { status: 'Normal' };
        }
        return { status: 'Normal' };
    }

    // For other vitals
    const value = parseFloat(reading);
    if (isNaN(value)) {
        console.log('Invalid numeric reading');
        return { status: 'invalid' };
    }

    console.log('Checking numeric vital:', { value, thresholds });

    // Check for low values first
    if (thresholds.low !== null && thresholds.low !== undefined && value < thresholds.low) {
        console.log('Value is low');
        return { status: 'Low' };
    }

    // Check for high values
    if (thresholds.high !== null && thresholds.high !== undefined && value > thresholds.high) {
        console.log('Value is high');
        return { status: 'High' };
    }

    // Normal range
    console.log('Value is normal');
    return { status: 'Normal' };
};

const openVitalDialog = () => {
    vitalForm.value = { selectedType: null, reading: '' };
    visible.value = true;
};

const cancelVital = () => {
    visible.value = false;
    vitalForm.value = { selectedType: null, reading: '' };
};

const submitVital = async () => {
    if (!isFormValid()) {
        toast.add({
            severity: 'warn',
            summary: 'Missing Information',
            detail: 'Please fill in all required fields',
            life: 3000
        });
        return;
    }

    submitting.value = true;
    try {
        const { data } = await addVitalLog({
            vitalTypeId: vitalForm.value.selectedType.value,
            reading: vitalForm.value.reading.trim(),
            loggedAt: new Date().toISOString()
        });

        const response = data?.addVitalLog;

        if (response?.status === 201) {
            toast.add({
                severity: 'success',
                summary: 'Vital Logged',
                detail: response.message || `${vitalForm.value.selectedType.label} reading recorded successfully`,
                life: 3000
            });

            // Refetch vital logs to update the list
            await refetch();
            cancelVital();
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to log vital. Please try again.',
                life: 3000
            });
        }
    } catch (error) {
        console.error('Error logging vital:', error);
        toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to log vital. Please try again.',
            life: 3000
        });
    } finally {
        submitting.value = false;
    }
};

const getVitalIcon = (vitalType) => {
    switch (vitalType.toLowerCase()) {
        case 'blood pressure':
            return 'pi pi-heart';
        case 'heart rate':
            return 'pi pi-heart-fill';
        case 'body temperature':
            return 'pi pi-sun';
        case 'blood sugar':
            return 'pi pi-chart-line';
        case 'weight':
            return 'pi pi-chart-bar';
        case 'oxygen saturation':
            return 'pi pi-circle';
        default:
            return 'pi pi-heart';
    }
};

const isFormValid = () => {
    return vitalForm.value.selectedType && vitalForm.value.reading.trim();
};

// Add helper function for status severity mapping
const getStatusSeverity = (status) => {
    switch (status) {
        case 'Normal':
            return 'success'; // Green
        case 'Low':
            return 'danger';  // Red
        case 'High':
            return 'danger';  // Red
        default:
            return 'secondary';
    }
};

// Move onMounted to the end and make sure it's properly defined
onMounted(() => {
    // Data is automatically fetched by useQuery
    console.log('VitalLogs component mounted with ezId:', props.ezId);
});
</script>

<template>
    <Toast />
    <div class="vital-logs-card">
        <Card class="w-full">
            <template #header>
                <div class="section-header">
                    <i class="pi pi-heart text-red-500"></i>
                    <h3 class="section-title">Vital Logs</h3>
                </div>
            </template>
            <template #content>
                <!-- Loading state -->
                <div v-if="loadingLogs || loadingTypes" class="text-center py-8">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                    <p class="mt-4">Loading vital logs...</p>
                </div>

                <!-- Error state -->
                <div v-else-if="error" class="text-center py-8">
                    <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
                    <p class="text-red-600">Failed to load vital logs</p>
                    <Button label="Retry" @click="refetch" class="mt-3" />
                </div>

                <!-- Content -->
                <div v-else>
                    <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
                        <p class="text-surface-600 dark:text-surface-400">
                            Track and monitor your vital signs over time to maintain good health.
                        </p>
                        <Button
                            label="Log New Vital"
                            icon="pi pi-plus"
                            severity="success"
                            outlined
                            @click="openVitalDialog"
                            class="flex-shrink-0"
                        />
                    </div>

                    <!-- Show message if no vital types available -->
                    <div v-if="vitalTypes.length === 0" class="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                        <div class="flex items-center gap-2 text-yellow-700 dark:text-yellow-300">
                            <i class="pi pi-exclamation-triangle"></i>
                            <div class="text-sm">
                                <p class="font-medium mb-1">No Vital Types Available</p>
                                <p>The vital types are loading. Please wait a moment.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Existing DataTable and empty state code -->
                    <DataTable
                        v-if="vitals && vitals.length"
                        :value="vitals"
                        :rows="8"
                        :paginator="vitals.length > 8"
                        responsiveLayout="scroll"
                        class="vital-logs-table"
                    >
                        <Column field="label" header="Vital Type" style="min-width: 150px">
                            <template #body="{ data }">
                                <div class="flex items-center gap-2">
                                    <i :class="getVitalIcon(data.label)" class="text-blue-500"></i>
                                    <span class="font-medium text-surface-900 dark:text-surface-0">{{ data.label }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="reading" header="Reading" style="min-width: 120px">
                            <template #body="{ data }">
                                <div class="text-lg font-semibold text-surface-800 dark:text-surface-200">
                                    {{ data.reading }}
                                    <span class="text-sm font-normal text-surface-500 dark:text-surface-400">{{ data.unit }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="date" header="Date" style="min-width: 100px" sortable>
                            <template #body="{ data }">
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-calendar text-green-500"></i>
                                    <span class="text-surface-700 dark:text-surface-300">{{ data.date }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="time" header="Time" style="min-width: 80px">
                            <template #body="{ data }">
                                <div class="flex items-center gap-2">
                                    <i class="pi pi-clock text-orange-500"></i>
                                    <span class="text-surface-700 dark:text-surface-300">{{ data.time }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column header="Status" style="min-width: 100px">
                            <template #body="{ data }">
                                <Tag
                                    v-if="data.statusInfo?.status && data.statusInfo.status !== 'irrelevant' && data.statusInfo.status !== 'invalid'"
                                    :value="data.statusInfo.status"
                                    :severity="getStatusSeverity(data.statusInfo.status)"
                                    class="text-sm font-medium"
                                />
                                <span v-else class="text-surface-400 dark:text-surface-500 text-sm">
                                    -
                                </span>
                            </template>
                        </Column>
                    </DataTable>

                    <div v-else class="empty-state">
                        <div class="text-center py-12">
                            <div class="text-surface-400 dark:text-surface-500 mb-4">
                                <i class="pi pi-heart text-6xl"></i>
                            </div>
                            <h4 class="text-xl font-medium text-surface-700 dark:text-surface-300 mb-2">
                                No Vital Logs Found
                            </h4>
                            <p class="text-surface-500 dark:text-surface-400 mb-4">
                                Start tracking your health by logging your first vital signs.
                            </p>
                            <Button
                                label="Log Your First Vital"
                                icon="pi pi-plus"
                                severity="success"
                                @click="openVitalDialog"
                            />
                        </div>
                    </div>
                </div>
            </template>
        </Card>

        <!-- Enhanced Vital Log Dialog -->
        <Dialog
            v-model:visible="visible"
            modal
            header="Log Vital Signs"
            :style="{ width: '500px' }"
            :closable="!submitting"
            :dismissableMask="!submitting"
            class="vital-log-dialog"
        >
            <template #header>
                <div class="dialog-header">
                    <i class="pi pi-heart-fill text-red-500 mr-2"></i>
                    <span>Log Vital Signs</span>
                </div>
            </template>

            <div class="dialog-content">
                <div class="grid formgrid p-fluid">
                    <div class="field col-12 mb-4">
                        <FloatLabel>
                            <Select
                                id="vitalType"
                                v-model="vitalForm.selectedType"
                                :options="vitalTypes"
                                optionLabel="label"
                                class="w-full"
                            />
                            <label for="vitalType">Select Vital Type *</label>
                        </FloatLabel>
                    </div>

                    <div class="field col-12 mb-4">
                        <Label>
                            <InputText
                                id="reading"
                                v-model="vitalForm.reading"
                                class="w-full"
                                :placeholder="selectedVitalType?.placeholder || 'Enter reading'"
                            />
                            <label for="reading">
                                Reading *
                                <span v-if="selectedVitalType" class="text-surface-500 dark:text-surface-400">
                                    ({{ selectedVitalType.unit }})
                                </span>
                            </label>
                        </Label>
                    </div>
                </div>

                <div class="info-section">
                    <div class="flex items-start gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <i class="pi pi-info-circle text-blue-500 mt-1"></i>
                        <div class="text-sm text-blue-700 dark:text-blue-300">
                            <p class="font-medium mb-1">Vital Logging Guidelines</p>
                            <ul class="space-y-1">
                                <li>• Record vitals at consistent times for accurate tracking</li>
                                <li>• Ensure your measuring devices are properly calibrated</li>
                                <li>• Date and time will be automatically recorded</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div v-if="selectedVitalType" class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-green-700 dark:text-green-300">
                        <i :class="getVitalIcon(selectedVitalType.label)" class="text-green-500"></i>
                        <span class="text-sm font-medium">
                            Selected: {{ selectedVitalType.label }}
                        </span>
                    </div>
                    <p class="text-xs text-green-600 dark:text-green-400 mt-1">
                        {{ selectedVitalType.placeholder }}
                    </p>
                </div>
            </div>

            <template #footer>
                <div class="flex justify-end gap-3 mt-4">
                    <Button
                        label="Cancel"
                        icon="pi pi-times"
                        outlined
                        @click="cancelVital"
                        :disabled="submitting"
                        class="flex-shrink-0"
                    />
                    <Button
                        label="Log Vital"
                        icon="pi pi-check"
                        severity="success"
                        @click="submitVital"
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
.vital-logs-card {
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

.vital-logs-table {
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

/* Dark mode enhancements */
:global(.p-dark) .vital-logs-card :deep(.p-card) {
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

    .field.mb-4 {
        margin-bottom: 1.25rem !important;
    }

    .dialog-content {
        padding: 1rem 0;
    }
}

/* Animation enhancements */
.vital-logs-table :deep(tr) {
    transition: all 0.3s ease;
}

.vital-logs-table :deep(tr:hover) {
    background: var(--surface-hover);
}

:deep(.p-button) {
    transition: all 0.3s ease;
}

:deep(.p-button:hover) {
    transform: translateY(-1px);
}

/* Enhanced status color overrides for better visibility */
:deep(.p-tag.p-tag-success) {
    background: #dcfce7; /* Light green background */
    color: #166534;      /* Dark green text */
    border: 1px solid #22c55e;
    font-weight: 600;
}

:deep(.p-tag.p-tag-danger) {
    background: #fee2e2; /* Light red background */
    color: #dc2626;      /* Dark red text */
    border: 1px solid #ef4444;
    font-weight: 600;
}

:deep(.p-tag.p-tag-warning) {
    background: var(--yellow-100);
    color: var(--yellow-800);
    border: 1px solid var(--yellow-300);
    font-weight: 600;
}

:deep(.p-tag.p-tag-secondary) {
    background: var(--surface-100);
    color: var(--surface-600);
    border: 1px solid var(--surface-300);
    font-weight: 600;
}

/* Dark mode enhancements */
:global(.p-dark) :deep(.p-tag.p-tag-success) {
    background: #14532d; /* Dark green background */
    color: #22c55e;      /* Light green text */
    border: 1px solid #16a34a;
}

:global(.p-dark) :deep(.p-tag.p-tag-danger) {
    background: #7f1d1d; /* Dark red background */
    color: #f87171;      /* Light red text */
    border: 1px solid #dc2626;
}

:global(.p-dark) :deep(.p-tag.p-tag-warning) {
    background: var(--yellow-900);
    color: var(--yellow-100);
    border: 1px solid var(--yellow-700);
}

:global(.p-dark) :deep(.p-tag.p-tag-secondary) {
    background: var(--surface-800);
    color: var(--surface-300);
    border: 1px solid var(--surface-600);
}
</style>
