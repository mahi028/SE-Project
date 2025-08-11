<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLoginStore } from '@/store/loginStore'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useLazyQuery } from '@vue/apollo-composable';
import gql from 'graphql-tag';
import InfoItem from '@/components/InfoItem.vue'
import VitalLogs from '@/components/seniorDashboard/VitalLogs.vue'
import VitalTrend from '@/components/VitalTrend.vue'

const route = useRoute()
const router = useRouter()
const loginStore = useLoginStore()
const showMedicalHistoryDialog = ref(false)
const showPrescriptionDialog = ref(false)
const showRoleMismatchDialog = ref(false)
const foundUser = ref(null)
const toast = useToast()
const confirm = useConfirm()

const GET_USER_DATA = gql`
  query getUser($ezId: String!) {
    getUser(ezId: $ezId) {
      ezId
      name
      email
      role
      phoneNum
      createdAt
      profileImageUrl
      senInfo {
        senId
        ezId
        gender
        dob
        address
        pincode
        alternatePhoneNum
        medicalInfo
        vitalLogs {
          logId
          senId
          vitalTypeId
          reading
          loggedAt
        }
      }
    }
  }
`;

const GET_APPOINTMENTS = gql`
  query GetAppointments($senId: String!, $docId: String!) {
    getAppointmentsForDoctorSenior(senId: $senId, docId: $docId) {
      appId
      senId
      docId
      remTime
      reason
      status
      createdAt
    }
  }
`;

const { load: fetchUser, result, loading: userLoading, error } = useLazyQuery(GET_USER_DATA)
const { load: fetchAppointments, result: appointmentsResult, loading: appointmentsLoading } = useLazyQuery(GET_APPOINTMENTS)

// Computed properties to extract data from GraphQL result
const userDetails = computed(() => {
  const user = result.value?.getUser
  if (!user) return null

  // Check if user role matches expected role (0 for senior)
  if (user.role !== 0) {
    foundUser.value = user
    showRoleMismatchDialog.value = true
    return null
  }

  return {
    name: user.name,
    email: user.email,
    ezId: user.ezId,
    phoneNum: user.phoneNum,
    address: user.senInfo?.address || '',
    pincode: user.senInfo?.pincode || '',
    alternatePhone: user.senInfo?.alternatePhoneNum || 'Not provided',
    profileImageUrl: user.profileImageUrl
  }
})

const appointments = computed(() => {
  return appointmentsResult.value?.getAppointmentsForDoctorSenior || []
})

const vitals = computed(() => {
  const vitalLogs = result.value?.getUser?.senInfo?.vitalLogs || []
  // Transform vital logs to match expected format
  return vitalLogs.map(log => ({
    id: log.logId,
    label: getVitalTypeLabel(log.vitalTypeId),
    reading: log.reading,
    unit: getVitalUnit(log.vitalTypeId),
    date: new Date(log.loggedAt).toLocaleDateString(),
    time: new Date(log.loggedAt).toLocaleTimeString(),
    statusInfo: determineVitalStatus(log.vitalTypeId, log.reading)
  }))
})

// Helper functions for vital data transformation
const getVitalTypeLabel = (vitalTypeId) => {
  const vitalTypes = {
    1: 'Blood Pressure',
    2: 'Heart Rate',
    3: 'Temperature',
    4: 'Blood Sugar',
    5: 'Weight',
    6: 'Oxygen Saturation'
  }
  return vitalTypes[vitalTypeId] || 'Unknown'
}

const getVitalUnit = (vitalTypeId) => {
  const units = {
    1: 'mmHg',
    2: 'bpm',
    3: '°F',
    4: 'mg/dL',
    5: 'kg',
    6: '%'
  }
  return units[vitalTypeId] || ''
}

const determineVitalStatus = (vitalTypeId, reading) => {
  // Simple status determination logic - can be enhanced
  const numReading = parseFloat(reading)

  switch(vitalTypeId) {
    case 2: // Heart Rate
      if (numReading < 60) return { status: 'Low' }
      if (numReading > 100) return { status: 'High' }
      return { status: 'Normal' }
    case 3: // Temperature
      if (numReading < 97) return { status: 'Low' }
      if (numReading > 99.5) return { status: 'High' }
      return { status: 'Normal' }
    case 6: // Oxygen Saturation
      if (numReading < 95) return { status: 'Low' }
      return { status: 'Normal' }
    default:
      return { status: 'irrelevant' }
  }
}

// Add method to get vital icons for doctor view
const getVitalIcon = (vitalType) => {
  switch (vitalType.toLowerCase()) {
    case 'blood pressure':
      return 'pi pi-heart'
    case 'heart rate':
      return 'pi pi-heart-fill'
    case 'temperature':
      return 'pi pi-sun'
    case 'blood sugar':
      return 'pi pi-chart-line'
    case 'weight':
      return 'pi pi-chart-bar'
    case 'oxygen saturation':
      return 'pi pi-circle'
    default:
      return 'pi pi-heart'
  }
}

onMounted(async () => {
  try {
    await fetchUser(GET_USER_DATA, { ezId: route.params.ezId })
    // console.log('user data:', result.value?.getUser)

    // Only fetch appointments if a doctor is viewing the senior's profile
    if (loginStore.role === 1) {
      await fetchAppointments(GET_APPOINTMENTS, {
        senId: route.params.ezId,
        docId: loginStore.ezId
      })
    }
  } catch (error) {
    console.error('Failed to load user data:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load profile data',
      life: 3000
    })
  }
})

const cancelAppointment = (appointment) => {
  confirm.require({
    message: `Are you sure you want to cancel the appointment with ${userDetails.value.name} on ${new Date(appointment.remTime).toLocaleDateString()}?`,
    header: 'Cancel Appointment',
    icon: 'pi pi-exclamation-triangle',
    rejectProps: {
      label: 'Keep Appointment',
      severity: 'secondary',
      outlined: true
    },
    acceptProps: {
      label: 'Cancel Appointment',
      severity: 'danger'
    },
    accept: async () => {
      try {
        // TODO: Implement GraphQL mutation for canceling appointment
        await new Promise(resolve => setTimeout(resolve, 500))

        toast.add({
          severity: 'success',
          summary: 'Appointment Cancelled',
          detail: 'The appointment has been cancelled successfully.',
          life: 3000
        })

        // Refetch appointments
        await fetchAppointments(GET_APPOINTMENTS, {
          senId: route.params.ezId,
          docId: loginStore.ezId
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to cancel appointment. Please try again.',
          life: 3000
        })
      }
    }
  })
}

const isUpcomingAppointment = (appointment) => {
  return new Date(appointment.remTime) >= new Date()
}

// Transform medical info for display
const medicalHistory = computed(() => {
  const medicalInfo = result.value?.getUser?.senInfo?.medicalInfo
  if (!medicalInfo) return []

  try {
    // Handle double-encoded JSON string from backend
    const parsedOnce = typeof medicalInfo === 'string' ? JSON.parse(medicalInfo) : medicalInfo
    const finalInfo = typeof parsedOnce === 'string' ? JSON.parse(parsedOnce) : parsedOnce

    return finalInfo.medicalConditions?.map((condition, index) => ({
      id: `MH${index + 1}`,
      date: condition.diagnosedYear ? `${condition.diagnosedYear}-01-01` : 'Unknown',
      condition: condition.name || 'Unknown condition',
      diagnosis: condition.name || 'Unknown diagnosis',
      treatment: 'As prescribed',
      doctor: 'Medical Professional',
      notes: condition.curingYear ? `Treatment until ${condition.curingYear}` : 'Ongoing treatment'
    })) || []
  } catch (e) {
    console.error('Error parsing medical info:', e)
    return []
  }
})

const prescriptions = computed(() => {
  const medicalInfo = result.value?.getUser?.senInfo?.medicalInfo
  if (!medicalInfo) return []

  try {
    // Handle double-encoded JSON string from backend
    const parsedOnce = typeof medicalInfo === 'string' ? JSON.parse(medicalInfo) : medicalInfo
    const finalInfo = typeof parsedOnce === 'string' ? JSON.parse(parsedOnce) : parsedOnce

    return finalInfo.medications?.map((med, index) => ({
      id: `RX${index + 1}`,
      date: med.startDate || 'Unknown',
      doctor: 'Medical Professional',
      medications: [{
        name: med.name || 'Unknown medication',
        strength: med.dosage || 'As prescribed',
        frequency: med.frequency || 'As directed',
        duration: med.endDate === '' ? 'Ongoing' : '30 days',
        instructions: med.route || 'Take as directed'
      }],
      notes: `Route: ${med.route || 'Not specified'}`
    })) || []
  } catch (e) {
    console.error('Error parsing medical info:', e)
    return []
  }
})

// Update dialog functions to use computed data
const viewMedicalHistory = async () => {
  showMedicalHistoryDialog.value = true
}

const viewPrescriptions = async () => {
  showPrescriptionDialog.value = true
}

const redirectToCorrectProfile = () => {
  if (foundUser.value) {
    const correctRoute = foundUser.value.role === 1 ? '/doctor/' : '/senior/'
    router.push(correctRoute + foundUser.value.ezId)
  }
  showRoleMismatchDialog.value = false
}

const closeRoleMismatchDialog = () => {
  showRoleMismatchDialog.value = false
  foundUser.value = null
}
</script>

<template>
  <Toast />
  <ConfirmDialog />
  <div class="p-4 max-w-7xl mx-auto">
    <Card class="w-full">
      <template #content>
        <!-- Loading state -->
        <div v-if="userLoading" class="text-center py-8">
          <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
          <p class="mt-4">Loading profile...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="text-center py-8">
          <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
          <p class="text-red-600">Failed to load profile data</p>
        </div>

        <!-- User not found state -->
        <div v-else-if="!userDetails && !showRoleMismatchDialog" class="text-center py-8">
          <i class="pi pi-user-times text-6xl text-gray-400 mb-4"></i>
          <h2 class="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-2">User Not Found</h2>
          <p class="text-gray-600 dark:text-gray-400">The senior citizen profile you're looking for could not be found.</p>
          <p class="text-gray-500 dark:text-gray-500 text-sm mt-2">The user may not exist or you may not have permission to view this profile.</p>
        </div>

        <!-- Profile content -->
        <div v-else-if="userDetails">
          <!-- Profile Header -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center mb-5">
            <!-- Profile Image -->
            <div class="flex justify-center">
              <img
                src="/images/user.png"
                alt="Profile Picture"
                class="w-64 h-64 object-cover rounded-xl shadow"
              />
            </div>

            <!-- Basic Details -->
            <div class="md:col-span-2">
              <h2 class="text-3xl font-bold mb-4">{{ userDetails.name }}</h2>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <InfoItem
                  type="basic"
                  label="Address"
                  :value="userDetails.address ? `${userDetails.address}, ${userDetails.pincode}` : 'Not provided'"
                />
                <InfoItem type="basic" label="Primary Phone" :value="userDetails.phoneNum" />
                <InfoItem type="basic" label="Alternate Phone" :value="userDetails.alternatePhone" />
                <InfoItem type="basic" label="Email" :value="userDetails.email" />
              </div>
            </div>
          </div>

          <!-- Doctor Action Buttons -->
          <div v-if="loginStore.role === 1" class="mb-8">
            <h3 class="text-2xl font-semibold mb-4 flex items-center gap-2">
              <i class="pi pi-user-md text-blue-500"></i>
              Medical Information
            </h3>
            <div class="flex flex-wrap gap-3">
              <Button
                label="View Medical History"
                icon="pi pi-file-text"
                severity="info"
                @click="viewMedicalHistory"
                class="flex-shrink-0"
              />
              <Button
                label="View Prescriptions"
                icon="pi pi-receipt"
                severity="success"
                @click="viewPrescriptions"
                class="flex-shrink-0"
              />
            </div>
            <Divider />
          </div>

          <!-- Appointment History Section -->
          <div class="mt-8" v-if="loginStore.role === 1">
            <h3 class="text-2xl font-semibold mb-6">Appointment History with {{ userDetails.name }}</h3>
            <div v-if="appointmentsLoading" class="text-center py-6">
              <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
            </div>
            <div v-else-if="appointments.length === 0" class="text-center py-10">
              <div class="text-gray-500 mb-3">
                <i class="pi pi-calendar-times text-5xl"></i>
              </div>
              <p class="text-gray-600 text-lg">No appointments found between you and this patient.</p>
            </div>
            <div v-else>
              <DataTable
                :value="appointments"
                :rows="10"
                :paginator="appointments.length > 10"
                responsiveLayout="scroll"
                class="p-datatable-lg text-base"
              >
                <Column field="remTime" header="Date & Time" sortable style="width: 35%">
                  <template #body="{ data }">
                    <div>
                      <div class="font-semibold text-base">{{ new Date(data.remTime).toLocaleDateString() }}</div>
                      <div class="text-sm text-surface-600">{{ new Date(data.remTime).toLocaleTimeString() }}</div>
                    </div>
                  </template>
                </Column>
                <Column field="reason" header="Reason" style="width: 50%">
                  <template #body="{ data }">
                    <span class="text-base">{{ data.reason || 'General consultation' }}</span>
                  </template>
                </Column>
                <Column header="Actions" style="width: 15%">
                  <template #body="{ data }">
                    <Button
                      v-if="isUpcomingAppointment(data)"
                      icon="pi pi-times"
                      size="small"
                      severity="danger"
                      outlined
                      @click="cancelAppointment(data)"
                      v-tooltip.top="'Cancel Appointment'"
                    />
                    <span v-else class="text-surface-500 text-sm">Completed</span>
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>

          <Divider v-if="loginStore.role === 1" />

          <!-- Vital Logs and Trends Section - Only for doctors -->
          <div v-if="loginStore.role === 1" class="mt-8 space-y-8">
            <!-- Vital Trends Chart -->
            <div>
              <h3 class="text-2xl font-semibold mb-6 flex items-center gap-2">
                <i class="pi pi-chart-line text-blue-500"></i>
                <span>{{ userDetails.name }}'s Vital Trends</span>
              </h3>
              <VitalTrend :ezId="route.params.ezId" />
            </div>

            <!-- Vital Logs Table -->
            <div>
              <h3 class="text-2xl font-semibold mb-6 flex items-center gap-2">
                <i class="pi pi-heart text-red-500"></i>
                <span>{{ userDetails.name }}'s Vital Logs</span>
              </h3>

              <div v-if="vitals.length === 0" class="text-center py-10">
                <div class="text-gray-500 mb-3">
                  <i class="pi pi-heart text-5xl"></i>
                </div>
                <p class="text-gray-600 text-lg">No vital logs found for this patient.</p>
              </div>
              <div v-else>
                <DataTable
                  :value="vitals"
                  :rows="10"
                  :paginator="vitals.length > 10"
                  responsiveLayout="scroll"
                  class="p-datatable-lg text-base"
                  sortField="date"
                  :sortOrder="-1"
                >
                  <Column field="label" header="Vital Type" style="width: 25%">
                    <template #body="{ data }">
                      <div class="flex items-center gap-2">
                        <i :class="getVitalIcon(data.label)" class="text-blue-500"></i>
                        <span class="text-base font-medium">{{ data.label }}</span>
                      </div>
                    </template>
                  </Column>
                  <Column field="reading" header="Reading" style="width: 20%">
                    <template #body="{ data }">
                      <span class="font-semibold text-base">{{ data.reading }} {{ data.unit }}</span>
                    </template>
                  </Column>
                  <Column field="date" header="Date" sortable style="width: 20%">
                    <template #body="{ data }">
                      <span class="text-base">{{ data.date }}</span>
                    </template>
                  </Column>
                  <Column field="time" header="Time" style="width: 20%">
                    <template #body="{ data }">
                      <span class="text-base">{{ data.time }}</span>
                    </template>
                  </Column>
                  <Column header="Status" style="width: 15%">
                    <template #body="{ data }">
                      <span
                        v-if="data.statusInfo?.status === 'irrelevant'"
                        class="text-gray-500 font-semibold text-base"
                      >
                        -
                      </span>
                      <Tag
                        v-else
                        :value="data.statusInfo?.status"
                        :severity="data.statusInfo?.status === 'Normal' ? 'success' :
                                  data.statusInfo?.status === 'High' ? 'danger' :
                                  data.statusInfo?.status === 'Low' ? 'warning' : 'secondary'"
                        class="text-sm"
                      />
                    </template>
                  </Column>
                </DataTable>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Role Mismatch Dialog -->
    <Dialog
      v-model:visible="showRoleMismatchDialog"
      modal
      header="Wrong Profile Type"
      :style="{ width: '500px' }"
      :closable="true"
      :dismissableMask="false"
    >
      <div class="flex items-start gap-4">
        <i class="pi pi-info-circle text-blue-500 text-2xl mt-1"></i>
        <div>
          <p class="mb-3">
            The user ID you're looking for belongs to a
            <strong>{{ foundUser?.role === 1 ? 'Doctor' : 'User' }}</strong>,
            not a Senior Citizen.
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Would you like to be redirected to their correct profile page?
          </p>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button
            label="Stay Here"
            icon="pi pi-times"
            outlined
            @click="closeRoleMismatchDialog"
          />
          <Button
            label="Go to Profile"
            icon="pi pi-external-link"
            severity="info"
            @click="redirectToCorrectProfile"
          />
        </div>
      </template>
    </Dialog>

    <!-- Medical History Dialog -->
    <Dialog
      v-model:visible="showMedicalHistoryDialog"
      modal
      header="Medical History"
      :style="{ width: '800px' }"
      class="medical-history-dialog"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-file-text text-blue-500"></i>
          <span class="text-xl font-semibold">{{ userDetails.name }}'s Medical History</span>
        </div>
      </template>

      <div class="space-y-4">
        <div v-if="medicalHistory.length === 0" class="text-center py-8">
          <i class="pi pi-file text-4xl text-surface-400 mb-3"></i>
          <p class="text-surface-500 dark:text-surface-400">No medical history records found.</p>
        </div>

        <Card
          v-for="record in medicalHistory"
          :key="record.id"
          class="medical-record-card"
        >
          <template #content>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Date</label>
                  <p class="text-surface-900 dark:text-surface-0 font-semibold">{{ record.date }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Condition</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.condition }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Diagnosis</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.diagnosis }}</p>
                </div>
              </div>
              <div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Treating Doctor</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.doctor }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Treatment</label>
                  <p class="text-surface-900 dark:text-surface-0">{{ record.treatment }}</p>
                </div>
                <div class="mb-3">
                  <label class="text-sm font-medium text-surface-600 dark:text-surface-400">Notes</label>
                  <p class="text-surface-700 dark:text-surface-300 text-sm">{{ record.notes }}</p>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <Button
            label="Close"
            icon="pi pi-times"
            outlined
            @click="showMedicalHistoryDialog = false"
          />
        </div>
      </template>
    </Dialog>

    <!-- Prescriptions Dialog -->
    <Dialog
      v-model:visible="showPrescriptionDialog"
      modal
      header="Prescriptions"
      :style="{ width: '900px' }"
      class="prescription-dialog"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-receipt text-green-500"></i>
          <span class="text-xl font-semibold">{{ userDetails.name }}'s Prescriptions</span>
        </div>
      </template>

      <div class="space-y-6">
        <div v-if="prescriptions.length === 0" class="text-center py-8">
          <i class="pi pi-receipt text-4xl text-surface-400 mb-3"></i>
          <p class="text-surface-500 dark:text-surface-400">No prescription records found.</p>
        </div>

        <Card
          v-for="prescription in prescriptions"
          :key="prescription.id"
          class="prescription-card"
        >
          <template #content>
            <div class="mb-4">
              <div class="flex justify-between items-start mb-3">
                <div>
                  <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0">
                    Prescription #{{ prescription.id }}
                  </h4>
                  <p class="text-surface-600 dark:text-surface-400">
                    Date: {{ prescription.date }} | Doctor: {{ prescription.doctor }}
                  </p>
                </div>
                <Tag value="Active" severity="success" />
              </div>

              <div class="medications-section">
                <h5 class="text-md font-semibold text-surface-900 dark:text-surface-0 mb-3">
                  Medications
                </h5>
                <div class="space-y-3">
                  <div
                    v-for="(medication, index) in prescription.medications"
                    :key="index"
                    class="medication-item p-3 bg-surface-50 dark:bg-surface-800 rounded-lg"
                  >
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Medicine</label>
                        <p class="text-surface-900 dark:text-surface-0 font-semibold">
                          {{ medication.name }} {{ medication.strength }}
                        </p>
                      </div>
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Frequency</label>
                        <p class="text-surface-900 dark:text-surface-0">{{ medication.frequency }}</p>
                      </div>
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Duration</label>
                        <p class="text-surface-900 dark:text-surface-0">{{ medication.duration }}</p>
                      </div>
                      <div>
                        <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Instructions</label>
                        <p class="text-surface-700 dark:text-surface-300 text-sm">{{ medication.instructions }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="prescription.notes" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <label class="text-sm font-medium text-blue-700 dark:text-blue-300">Doctor's Notes</label>
                <p class="text-blue-800 dark:text-blue-200 text-sm">{{ prescription.notes }}</p>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <Button
            label="Close"
            icon="pi pi-times"
            outlined
            @click="showPrescriptionDialog = false"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
a:hover {
  opacity: 0.8;
}

.medical-record-card,
.prescription-card {
  border-left: 4px solid var(--primary-500);
}

.medications-section {
  border-top: 1px solid var(--surface-border);
  padding-top: 1rem;
}

.medication-item {
  border: 1px solid var(--surface-border);
}

/* Dark mode enhancements */
:global(.p-dark) .medical-history-dialog :deep(.p-dialog),
:global(.p-dark) .prescription-dialog :deep(.p-dialog) {
  background: var(--surface-card);
}
</style>
