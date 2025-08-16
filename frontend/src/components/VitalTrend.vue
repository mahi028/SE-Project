<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useQuery } from '@vue/apollo-composable';
import gql from 'graphql-tag';
import Chart from 'primevue/chart';

const props = defineProps({
    ezId: {
        type: String,
        required: true
    }
});

const selectedVitalType = ref(1); // Default to Blood Pressure
const loading = ref(false);
const chartData = ref({});
const chartOptions = ref({});

// GraphQL queries
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
    query GetVitalLogs($senId: Int!, $vitalTypeId: Int) {
        getVitalLogs(senId: $senId, vitalTypeId: $vitalTypeId) {
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

const GET_USER_DATA = gql`
    query GetUser($ezId: String!) {
        getUser(ezId: $ezId) {
            senInfo {
                senId
            }
        }
    }
`;

// Apollo composables
const { result: vitalTypesResult, loading: loadingTypes } = useQuery(GET_VITAL_TYPES);
const { result: userResult, loading: loadingUser } = useQuery(GET_USER_DATA, {
    ezId: props.ezId
});

const senId = computed(() => userResult.value?.getUser?.senInfo?.senId);

const { result: vitalLogsResult, loading: loadingLogs, refetch } = useQuery(GET_VITAL_LOGS, {
    senId: senId,
    vitalTypeId: selectedVitalType
}, {
    enabled: computed(() => !!senId.value)
});

const vitalTypes = computed(() => {
    const types = vitalTypesResult.value?.getVitalTypes || [];
    return types.map(type => ({
        label: type.label,
        value: type.typeId,
        unit: type.unit,
        threshold: parseThreshold(type.threshold)
    }));
});

const vitals = computed(() => {
    return vitalLogsResult.value?.getVitalLogs || [];
});

const filteredVitals = computed(() => {
    return vitals.value
        .filter(vital => vital.vitalTypeId === selectedVitalType.value)
        .sort((a, b) => new Date(a.loggedAt) - new Date(b.loggedAt));
});

const selectedVitalTypeInfo = computed(() => {
    return vitalTypes.value.find(type => type.value === selectedVitalType.value);
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

const processChartData = () => {
    const filtered = filteredVitals.value;

    if (filtered.length === 0) {
        chartData.value = {
            labels: [],
            datasets: []
        };
        return;
    }

    const labels = filtered.map(vital => {
        const date = new Date(vital.loggedAt);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    });

    let datasets = [];
    const thresholds = selectedVitalTypeInfo.value?.threshold;

    if (selectedVitalType.value === 1) { // Blood Pressure
        const systolicData = [];
        const diastolicData = [];

        filtered.forEach(vital => {
            const match = vital.reading.match(/(\d+)\/(\d+)/);
            if (match) {
                systolicData.push(parseInt(match[1]));
                diastolicData.push(parseInt(match[2]));
            }
        });

        datasets = [
            {
                label: 'Systolic',
                data: systolicData,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: false,
                pointRadius: 4,
                pointHoverRadius: 6
            },
            {
                label: 'Diastolic',
                data: diastolicData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: false,
                pointRadius: 4,
                pointHoverRadius: 6
            }
        ];

        // Add threshold lines for blood pressure
        if (thresholds?.systolic) {
            datasets.push({
                label: 'Systolic High Threshold',
                data: Array(labels.length).fill(thresholds.systolic.high),
                borderColor: '#dc2626',
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                pointRadius: 0,
                tension: 0
            });
        }
        if (thresholds?.diastolic) {
            datasets.push({
                label: 'Diastolic High Threshold',
                data: Array(labels.length).fill(thresholds.diastolic.high),
                borderColor: '#1d4ed8',
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                pointRadius: 0,
                tension: 0
            });
        }
    } else {
        // Regular vitals
        const data = filtered.map(vital => parseFloat(vital.reading));

        datasets = [{
            label: selectedVitalTypeInfo.value?.label || 'Value',
            data: data,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4,
            fill: true,
            pointRadius: 4,
            pointHoverRadius: 6
        }];

        // Add threshold lines
        if (thresholds?.high !== null && thresholds?.high !== undefined) {
            datasets.push({
                label: 'High Threshold',
                data: Array(labels.length).fill(thresholds.high),
                borderColor: '#dc2626',
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                pointRadius: 0,
                tension: 0
            });
        }
        if (thresholds?.low !== null && thresholds?.low !== undefined) {
            datasets.push({
                label: 'Low Threshold',
                data: Array(labels.length).fill(thresholds.low),
                borderColor: '#f59e0b',
                backgroundColor: 'transparent',
                borderDash: [5, 5],
                pointRadius: 0,
                tension: 0
            });
        }
    }

    chartData.value = {
        labels: labels,
        datasets: datasets
    };
};

const setupChartOptions = () => {
    const vitalInfo = selectedVitalTypeInfo.value;

    chartOptions.value = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: `${vitalInfo?.label || 'Vital'} Trend Over Time`,
                font: {
                    size: 18,
                    weight: 'bold'
                },
                color: '#374151'
            },
            legend: {
                display: true,
                position: 'top',
                labels: {
                    usePointStyle: true,
                    filter: function(legendItem) {
                        // Hide threshold lines from legend if desired
                        return !legendItem.text.includes('Threshold');
                    }
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                callbacks: {
                    label: function(context) {
                        const unit = vitalInfo?.unit || '';
                        return `${context.dataset.label}: ${context.parsed.y} ${unit}`;
                    }
                }
            }
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Date & Time',
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                grid: {
                    display: false
                },
                ticks: {
                    maxRotation: 45
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: `${vitalInfo?.label || 'Value'} (${vitalInfo?.unit || ''})`,
                    font: {
                        size: 14,
                        weight: 'bold'
                    }
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.1)'
                },
                beginAtZero: false
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        },
        animation: {
            duration: 750,
            easing: 'easeInOutQuart'
        }
    };
};

const onVitalTypeChange = () => {
    if (senId.value) {
        refetch({
            senId: senId.value,
            vitalTypeId: selectedVitalType.value
        });
    }
};

const getStatistics = computed(() => {
    const filtered = filteredVitals.value;
    if (filtered.length === 0) return null;

    if (selectedVitalType.value === 1) { // Blood Pressure
        const latest = filtered[filtered.length - 1];
        const match = latest.reading.match(/(\d+)\/(\d+)/);
        return {
            totalReadings: filtered.length,
            latest: latest.reading,
            dateRange: {
                start: new Date(filtered[0].loggedAt).toLocaleDateString(),
                end: new Date(filtered[filtered.length - 1].loggedAt).toLocaleDateString()
            }
        };
    } else {
        const values = filtered.map(v => parseFloat(v.reading)).filter(v => !isNaN(v));
        const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
        const min = Math.min(...values);
        const max = Math.max(...values);

        return {
            totalReadings: filtered.length,
            latest: filtered[filtered.length - 1].reading,
            average: avg.toFixed(1),
            min: min.toString(),
            max: max.toString(),
            dateRange: {
                start: new Date(filtered[0].loggedAt).toLocaleDateString(),
                end: new Date(filtered[filtered.length - 1].loggedAt).toLocaleDateString()
            }
        };
    }
});

watch([selectedVitalType, senId], () => {
    onVitalTypeChange();
}, { immediate: false });

watch([filteredVitals, selectedVitalTypeInfo], () => {
    processChartData();
    setupChartOptions();
}, { immediate: true });

onMounted(() => {
    if (senId.value) {
        onVitalTypeChange();
    }
});
</script>

<template>
    <div class="card">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
            <h3 class="text-2xl font-semibold text-gray-800 dark:text-gray-200">Vital Trends</h3>
            <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
                <label for="vitalTypeSelect" class="text-base font-medium text-gray-700 dark:text-gray-300">
                    Select Vital:
                </label>
                <Dropdown
                    id="vitalTypeSelect"
                    v-model="selectedVitalType"
                    :options="vitalTypes"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Select vital type"
                    class="w-48"
                    :loading="loadingTypes"
                />
                <Button
                    icon="pi pi-refresh"
                    @click="onVitalTypeChange"
                    rounded
                    outlined
                    size="small"
                    v-tooltip.top="'Refresh data'"
                    :loading="loadingLogs"
                />
            </div>
        </div>

        <div v-if="loadingUser || loadingTypes || loadingLogs" class="text-center py-8">
            <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
            <p class="text-gray-600 dark:text-gray-400 mt-3">Loading vital trends...</p>
        </div>

        <div v-else-if="!senId" class="text-center py-12">
            <div class="text-gray-500 dark:text-gray-400 mb-3">
                <i class="pi pi-user-times text-5xl"></i>
            </div>
            <p class="text-gray-600 dark:text-gray-400 text-lg">
                Unable to load patient data
            </p>
        </div>

        <div v-else-if="filteredVitals.length === 0" class="text-center py-12">
            <div class="text-gray-500 dark:text-gray-400 mb-3">
                <i class="pi pi-chart-line text-5xl"></i>
            </div>
            <p class="text-gray-600 dark:text-gray-400 text-lg">
                No data available for {{ selectedVitalTypeInfo?.label || 'selected vital' }}
            </p>
            <p class="text-gray-500 dark:text-gray-500 text-sm mt-2">
                Patient needs to start logging vitals to see trends here
            </p>
        </div>

        <div v-else class="chart-container">
            <Chart
                type="line"
                :data="chartData"
                :options="chartOptions"
                class="chart"
            />

            <!-- Enhanced Summary Statistics -->
            <div class="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg border border-blue-200 dark:border-blue-700">
                    <div class="text-sm text-blue-600 dark:text-blue-400 font-medium mb-1">Total Readings</div>
                    <div class="text-3xl font-bold text-blue-800 dark:text-blue-300">
                        {{ getStatistics?.totalReadings }}
                    </div>
                </div>

                <div class="bg-green-50 dark:bg-green-900/20 p-6 rounded-lg border border-green-200 dark:border-green-700">
                    <div class="text-sm text-green-600 dark:text-green-400 font-medium mb-1">Latest Reading</div>
                    <div class="text-2xl font-bold text-green-800 dark:text-green-300">
                        {{ getStatistics?.latest }}
                        <span class="text-lg">{{ selectedVitalTypeInfo?.unit }}</span>
                    </div>
                </div>

                <div v-if="selectedVitalType !== 1" class="bg-purple-50 dark:bg-purple-900/20 p-6 rounded-lg border border-purple-200 dark:border-purple-700">
                    <div class="text-sm text-purple-600 dark:text-purple-400 font-medium mb-1">Average</div>
                    <div class="text-2xl font-bold text-purple-800 dark:text-purple-300">
                        {{ getStatistics?.average }}
                        <span class="text-lg">{{ selectedVitalTypeInfo?.unit }}</span>
                    </div>
                </div>

                <div class="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg border border-gray-200 dark:border-gray-600">
                    <div class="text-sm text-gray-600 dark:text-gray-400 font-medium mb-1">Date Range</div>
                    <div class="text-sm font-bold text-gray-800 dark:text-gray-300">
                        <div>{{ getStatistics?.dateRange.start }}</div>
                        <div class="text-xs text-gray-500 dark:text-gray-400">to</div>
                        <div>{{ getStatistics?.dateRange.end }}</div>
                    </div>
                </div>
            </div>

            <!-- Range Statistics for non-BP vitals -->
            <div v-if="selectedVitalType !== 1 && getStatistics" class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg border border-orange-200 dark:border-orange-700">
                    <div class="text-sm text-orange-600 dark:text-orange-400 font-medium mb-1">Minimum</div>
                    <div class="text-xl font-bold text-orange-800 dark:text-orange-300">
                        {{ getStatistics.min }} {{ selectedVitalTypeInfo?.unit }}
                    </div>
                </div>
                <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-700">
                    <div class="text-sm text-red-600 dark:text-red-400 font-medium mb-1">Maximum</div>
                    <div class="text-xl font-bold text-red-800 dark:text-red-300">
                        {{ getStatistics.max }} {{ selectedVitalTypeInfo?.unit }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.chart-container {
    width: 100%;
}

.chart {
    height: 450px;
    width: 100%;
}

@media (max-width: 768px) {
    .chart {
        height: 350px;
    }
}

/* Dark mode card styling */
.card {
    background: var(--surface-card);
    border: 1px solid var(--surface-border);
    border-radius: 12px;
    padding: 1.5rem;
}

/* Enhanced responsive grid */
@media (max-width: 640px) {
    .chart {
        height: 300px;
    }

    .grid {
        grid-template-columns: 1fr;
    }
}

@media (min-width: 641px) and (max-width: 1024px) {
    .grid.lg\\:grid-cols-4 {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
