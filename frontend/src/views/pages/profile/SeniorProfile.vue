<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLoginStore } from '@/store/loginStore'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { useLazyQuery, useMutation } from '@vue/apollo-composable';
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
        prescriptions {
          presId
          senId
          docId
          medicationData
          time
          instructions
          createdAt
        }
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

// Update prescriptions computed property to use the extended query data
const prescriptions = computed(() => {
  const prescriptionsData = result.value?.getUser?.senInfo?.prescriptions || []
  
  return prescriptionsData.map(prescription => {
    const timeData = typeof prescription.time === 'string'
      ? JSON.parse(prescription.time)
      : prescription.time

    // Determine if it's doctor-prescribed or self-added
    const isDoctorPrescribed = prescription.docId !== null && prescription.docId !== undefined

    return {
      id: `RX${prescription.presId}`,
      date: new Date(prescription.createdAt).toLocaleDateString() || 'Unknown',
      doctor: isDoctorPrescribed ? 'Prescribed by Doctor' : 'Self-Added',
      isPrescribed: isDoctorPrescribed,
      medications: [{
        name: prescription.medicationData || 'Unknown medication',
        strength: 'As prescribed',
        frequency: timeData?.frequency || 'As directed',
        duration: 'Ongoing',
        instructions: prescription.instructions || 'Take as directed'
      }],
      notes: `Schedule: ${timeData?.frequency || 'As needed'} at ${timeData?.times?.join(', ') || 'specified times'}`,
      rawData: prescription
    }
  })
})

// Add prescription form state
const showAddPrescriptionDialog = ref(false)
const submittingPrescription = ref(false)
const prescriptionForm = ref({
  medicationData: '',
  frequency: 'Daily',
  times: [new Date()],
  instructions: ''
})

const frequencyOptions = [
  { label: 'Daily', value: 'Daily' },
  { label: 'Weekly', value: 'Weekly' },
  { label: 'Monday', value: 'Monday' },
  { label: 'Tuesday', value: 'Tuesday' },
  { label: 'Wednesday', value: 'Wednesday' },
  { label: 'Thursday', value: 'Thursday' },
  { label: 'Friday', value: 'Friday' },
  { label: 'Saturday', value: 'Saturday' },
  { label: 'Sunday', value: 'Sunday' },
  { label: 'As Needed', value: 'As Needed' }
]

// Add prescription mutation
const ADD_PRESCRIPTION = gql`
  mutation AddPrescription($senId: Int!, $medicationData: String!, $time: JSONString!, $instructions: String!) {
    addPrescription(senId: $senId, medicationData: $medicationData, time: $time, instructions: $instructions) {
      message
      status
    }
  }
`

const { mutate: addPrescriptionMutation } = useMutation(ADD_PRESCRIPTION)

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

// Add appointment status helper
const getAppointmentStatusInfo = (appointment) => {
    const appointmentDateTime = new Date(appointment.remTime);
    const now = new Date();

    switch (appointment.status) {
        case 0:
            return { label: 'Pending', severity: 'warning', canCancel: true };
        case 1:
            if (appointmentDateTime < now) {
                return { label: 'Completed', severity: 'success', canCancel: false };
            } else {
                return { label: 'Confirmed', severity: 'success', canCancel: true };
            }
        case -1:
            return { label: 'Cancelled', severity: 'danger', canCancel: false };
        default:
            return { label: 'Unknown', severity: 'secondary', canCancel: false };
    }
};

// Add prescription management functions
const openAddPrescriptionDialog = () => {
  prescriptionForm.value = {
    medicationData: '',
    frequency: 'Daily',
    times: [new Date()],
    instructions: ''
  }
  showAddPrescriptionDialog.value = true
}

const cancelAddPrescription = () => {
  showAddPrescriptionDialog.value = false
  prescriptionForm.value = {
    medicationData: '',
    frequency: 'Daily',
    times: [new Date()],
    instructions: ''
  }
}

const addPrescriptionTime = () => {
  prescriptionForm.value.times.push(new Date())
}

const removePrescriptionTime = (index) => {
  if (prescriptionForm.value.times.length > 1) {
    prescriptionForm.value.times.splice(index, 1)
  }
}

const formatTimeForBackend = (timeDate) => {
  const hours = timeDate.getHours().toString().padStart(2, '0')
  const minutes = timeDate.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const isPrescriptionFormValid = () => {
  return prescriptionForm.value.medicationData.trim() &&
         prescriptionForm.value.frequency &&
         prescriptionForm.value.times.length > 0 &&
         prescriptionForm.value.instructions.trim()
}

const submitPrescription = async () => {
  if (!isPrescriptionFormValid()) {
    toast.add({
      severity: 'warn',
      summary: 'Missing Information',
      detail: 'Please fill in all required fields',
      life: 3000
    })
    return
  }

  submittingPrescription.value = true
  try {
    // Convert time Date objects to string format
    const timesArray = prescriptionForm.value.times.map(timeDate => formatTimeForBackend(timeDate))

    const timeData = {
      frequency: prescriptionForm.value.frequency,
      times: timesArray
    }

    const senId = result.value?.getUser?.senInfo?.senId
    if (!senId) {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Senior information not available',
        life: 3000
      })
      return
    }

    const { data } = await addPrescriptionMutation({
      senId: senId,
      medicationData: prescriptionForm.value.medicationData.trim(),
      time: JSON.stringify(timeData),
      instructions: prescriptionForm.value.instructions.trim()
    })

    const response = data?.addPrescription

    if (response?.status === 201) {
      toast.add({
        severity: 'success',
        summary: 'Prescription Added',
        detail: response.message || `Prescription for ${prescriptionForm.value.medicationData} has been added successfully!`,
        life: 3000
      })

      // Refetch user data to update prescriptions
      await fetchUser(GET_USER_DATA, { ezId: route.params.ezId })
      cancelAddPrescription()
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: response?.message || 'Failed to add prescription. Please try again.',
        life: 3000
      })
    }
  } catch (error) {
    console.error('Error adding prescription:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to add prescription. Please try again.',
      life: 3000
    })
  } finally {
    submittingPrescription.value = false
  }
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
                <Column field="remTime" header="Date & Time" sortable style="width: 30%">
                  <template #body="{ data }">
                    <div>
                      <div class="font-semibold text-base">{{ new Date(data.remTime).toLocaleDateString() }}</div>
                      <div class="text-sm text-surface-600">{{ new Date(data.remTime).toLocaleTimeString() }}</div>
                    </div>
                  </template>
                </Column>
                <Column field="reason" header="Reason" style="width: 40%">
                  <template #body="{ data }">
                    <span class="text-base">{{ data.reason || 'General consultation' }}</span>
                  </template>
                </Column>
                <Column header="Status" style="width: 15%">
                  <template #body="{ data }">
                    <Tag
                      :value="getAppointmentStatusInfo(data).label"
                      :severity="getAppointmentStatusInfo(data).severity"
                      class="text-sm"
                    />
                  </template>
                </Column>
                <Column header="Actions" style="width: 15%">
                  <template #body="{ data }">
                    <Button
                      v-if="getAppointmentStatusInfo(data).canCancel && loginStore.role === 1"
                      icon="pi pi-times"
                      size="small"
                      severity="danger"
                      outlined
                      @click="cancelAppointment(data)"
                      v-tooltip.top="'Cancel Appointment'"
                    />
                    <span v-else class="text-surface-500 text-sm">
                      {{ data.status === -1 ? 'Cancelled' :
                         data.status === 1 && !isUpcomingAppointment(data) ? 'Completed' :
                         data.status === 0 ? 'Pending' : 'No actions' }}
                    </span>
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
          <span class="text-xl font-semibold">{{ userDetails.name }}'s Medications</span>
        </div>
      </template>

      <div class="space-y-6">
        <!-- Add Prescription Button for Doctors -->
        <div v-if="loginStore.role === 1" class="flex justify-between items-center">
          <p class="text-surface-600 dark:text-surface-400">
            Current medications and prescriptions for {{ userDetails.name }}
          </p>
          <Button
            label="Prescribe New Medication"
            icon="pi pi-plus"
            severity="success"
            @click="openAddPrescriptionDialog"
            class="flex-shrink-0"
          />
        </div>

        <div v-if="prescriptions.length === 0" class="text-center py-8">
          <i class="pi pi-receipt text-4xl text-surface-400 mb-3"></i>
          <p class="text-surface-500 dark:text-surface-400">No medication records found.</p>
          <Button 
            v-if="loginStore.role === 1" 
            label="Add First Prescription" 
            icon="pi pi-plus" 
            severity="success" 
            @click="openAddPrescriptionDialog"
            class="mt-3"
          />
        </div>

        <!-- Group prescriptions by type -->
        <div v-else class="space-y-4">
          <!-- Doctor Prescribed Medications -->
          <div v-if="prescriptions.filter(p => p.isPrescribed).length > 0">
            <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-3 flex items-center gap-2">
              <i class="pi pi-user-md text-blue-500"></i>
              Doctor Prescribed Medications
            </h4>
            <div class="space-y-3">
              <Card
                v-for="prescription in prescriptions.filter(p => p.isPrescribed)"
                :key="prescription.id"
                class="prescription-card prescribed-card"
              >
                <template #content>
                  <div class="mb-4">
                    <div class="flex justify-between items-start mb-3">
                      <div>
                        <h5 class="text-md font-semibold text-surface-900 dark:text-surface-0">
                          {{ prescription.medications[0].name }}
                        </h5>
                        <p class="text-surface-600 dark:text-surface-400 text-sm">
                          Prescribed on: {{ prescription.date }}
                        </p>
                      </div>
                      <div class="flex items-center gap-2">
                        <Tag value="Doctor Prescribed" severity="success" />
                      </div>
                    </div>

                    <div class="medication-details">
                      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Frequency</label>
                          <p class="text-surface-900 dark:text-surface-0">{{ prescription.medications[0].frequency }}</p>
                        </div>
                        <div>
                          <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Duration</label>
                          <p class="text-surface-900 dark:text-surface-0">{{ prescription.medications[0].duration }}</p>
                        </div>
                        <div>
                          <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Instructions</label>
                          <p class="text-surface-700 dark:text-surface-300 text-sm">{{ prescription.medications[0].instructions }}</p>
                        </div>
                      </div>
                    </div>

                    <div v-if="prescription.notes" class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <label class="text-sm font-medium text-blue-700 dark:text-blue-300">Schedule Notes</label>
                      <p class="text-blue-800 dark:text-blue-200 text-sm">{{ prescription.notes }}</p>
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </div>

          <!-- Self-Added Medications -->
          <div v-if="prescriptions.filter(p => !p.isPrescribed).length > 0">
            <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-3 flex items-center gap-2">
              <i class="pi pi-user text-green-500"></i>
              Self-Added Medications
            </h4>
            <div class="space-y-3">
              <Card
                v-for="prescription in prescriptions.filter(p => !p.isPrescribed)"
                :key="prescription.id"
                class="prescription-card self-added-card"
              >
                <template #content>
                  <div class="mb-4">
                    <div class="flex justify-between items-start mb-3">
                      <div>
                        <h5 class="text-md font-semibold text-surface-900 dark:text-surface-0">
                          {{ prescription.medications[0].name }}
                        </h5>
                        <p class="text-surface-600 dark:text-surface-400 text-sm">
                          Added on: {{ prescription.date }}
                        </p>
                      </div>
                      <div class="flex items-center gap-2">
                        <Tag value="Self-Added" severity="info" />
                      </div>
                    </div>

                    <div class="medication-details">
                      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Frequency</label>
                          <p class="text-surface-900 dark:text-surface-0">{{ prescription.medications[0].frequency }}</p>
                        </div>
                        <div>
                          <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Duration</label>
                          <p class="text-surface-900 dark:text-surface-0">{{ prescription.medications[0].duration }}</p>
                        </div>
                        <div>
                          <label class="text-xs font-medium text-surface-600 dark:text-surface-400">Instructions</label>
                          <p class="text-surface-700 dark:text-surface-300 text-sm">{{ prescription.medications[0].instructions }}</p>
                        </div>
                      </div>
                    </div>

                    <div v-if="prescription.notes" class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <label class="text-sm font-medium text-green-700 dark:text-green-300">Schedule Notes</label>
                      <p class="text-green-800 dark:text-green-200 text-sm">{{ prescription.notes }}</p>
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </div>
        </div>
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

    <!-- Add Prescription Dialog -->
    <Dialog
      v-model:visible="showAddPrescriptionDialog"
      modal
      header="Add Prescription"
      :style="{ width: '700px' }"
      :closable="!submittingPrescription"
      :dismissableMask="!submittingPrescription"
      class="add-prescription-dialog"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-plus-circle text-green-500"></i>
          <span class="text-xl font-semibold">Add Prescription for {{ userDetails.name }}</span>
        </div>
      </template>

      <div class="space-y-6">
        <!-- Patient Information Panel -->
        <Panel header="Patient Information" class="patient-info-panel">
          <div class="flex items-center gap-4 p-4">
            <Avatar
              :label="userDetails.name?.charAt(0) || 'P'"
              class="bg-blue-500 text-white text-xl"
              shape="circle"
              size="large"
            />
            <div class="flex-1">
              <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-1">
                {{ userDetails.name }}
              </h4>
              <p class="text-surface-600 dark:text-surface-400 text-sm">
                ID: {{ userDetails.ezId }} • Address: {{ userDetails.address || 'Not provided' }}
              </p>
            </div>
          </div>
        </Panel>

        <div class="grid formgrid p-fluid">
          <div class="field col-12 mb-4">
            <label for="medicationName" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              Medication Name *
            </label>
            <InputText
              id="medicationName"
              v-model="prescriptionForm.medicationData"
              placeholder="Enter medication name and dosage (e.g., Metformin 500mg)"
              class="w-full"
            />
          </div>

          <div class="field col-12 mb-4">
            <label for="frequency" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              Frequency *
            </label>
            <Select
              id="frequency"
              v-model="prescriptionForm.frequency"
              :options="frequencyOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Select frequency"
              class="w-full"
            />
          </div>

          <div class="field col-12 mb-4">
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-3">
              Medication Times *
            </label>

            <div class="space-y-3">
              <div v-for="(timeDate, index) in prescriptionForm.times" :key="index" class="flex items-center gap-2">
                <Calendar
                  v-model="prescriptionForm.times[index]"
                  timeOnly
                  hourFormat="12"
                  showIcon
                  placeholder="Select time"
                  class="flex-1"
                />
                <Button
                  v-if="prescriptionForm.times.length > 1"
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  outlined
                  @click="removePrescriptionTime(index)"
                  v-tooltip.top="'Remove time'"
                />
              </div>
            </div>

            <div class="mt-3">
              <Button
                label="Add Time"
                icon="pi pi-plus"
                size="small"
                outlined
                @click="addPrescriptionTime"
              />
            </div>
          </div>

          <div class="field col-12 mb-4">
            <label for="instructions" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
              Instructions *
            </label>
            <Textarea
              id="instructions"
              v-model="prescriptionForm.instructions"
              rows="3"
              class="w-full"
              placeholder="Enter detailed instructions (e.g., Take with food, after meals, etc.)"
              :maxlength="500"
            />
            <small class="text-surface-500 dark:text-surface-400 mt-1">
              {{ prescriptionForm.instructions.length }}/500 characters
            </small>
          </div>
        </div>

        <!-- Prescription Preview -->
        <div v-if="isPrescriptionFormValid()" class="prescription-preview">
          <Panel header="Prescription Preview" class="preview-panel">
            <div class="p-4 space-y-3">
              <div class="flex justify-between">
                <span class="font-medium">Medication:</span>
                <span>{{ prescriptionForm.medicationData }}</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium">Frequency:</span>
                <span>{{ prescriptionForm.frequency }}</span>
              </div>
              <div class="flex justify-between">
                <span class="font-medium">Times:</span>
                <span>{{ prescriptionForm.times.map(t => formatTimeForBackend(t)).join(', ') }}</span>
              </div>
              <Divider />
              <div>
                <span class="font-medium">Instructions:</span>
                <p class="mt-1 text-sm">{{ prescriptionForm.instructions }}</p>
              </div>
            </div>
          </Panel>
        </div>

        <!-- Medical Guidelines -->
        <div class="info-section">
          <div class="flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
            <i class="pi pi-info-circle text-amber-500 mt-1"></i>
            <div class="text-sm text-amber-700 dark:text-amber-300">
              <p class="font-medium mb-1">Prescription Guidelines</p>
              <ul class="space-y-1">
                <li>• Include complete medication name and dosage</li>
                <li>• Specify clear timing and frequency instructions</li>
                <li>• Add any special instructions (with food, before meals, etc.)</li>
                <li>• Patient will receive automatic reminders based on the schedule</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button
            label="Cancel"
            icon="pi pi-times"
            outlined
            @click="cancelAddPrescription"
            :disabled="submittingPrescription"
          />
          <Button
            label="Add Prescription"
            icon="pi pi-check"
            severity="success"
            @click="submitPrescription"
            :loading="submittingPrescription"
            :disabled="!isPrescriptionFormValid()"
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

.add-prescription-dialog :deep(.p-dialog-content) {
  padding: 1.5rem;
}

.patient-info-panel :deep(.p-panel-content) {
  padding: 0;
}

.preview-panel :deep(.p-panel-content) {
  padding: 0;
  background: var(--surface-50);
  border-radius: 8px;
}

:global(.p-dark) .preview-panel :deep(.p-panel-content) {
  background: var(--surface-800);
}

.prescription-preview {
  margin-top: 1.5rem;
}

.info-section {
  margin-top: 1.5rem;
}

/* Form field spacing */
.field.mb-4 {
  margin-bottom: 1.5rem !important;
}

/* Time picker styling */
:deep(.p-calendar) {
  width: 100%;
}

:deep(.p-calendar .p-inputtext) {
  text-align: center;
  font-family: monospace;
  font-size: 1rem;
  font-weight: 500;
}

/* Enhanced medication card styling */
.prescription-card {
  border-left: 4px solid var(--green-500);
}

.prescription-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

:global(.p-dark) .prescription-card:hover {
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.1);
}

/* Enhanced prescribed and self-added card styling */
.prescribed-card {
  border-left: 4px solid var(--blue-500);
}

.self-added-card {
  border-left: 4px solid var(--green-500);
}

.prescribed-card:hover {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transition: all 0.3s ease;
}

.self-added-card:hover {
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);
  transition: all 0.3s ease;
}

:global(.p-dark) .prescribed-card:hover {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

:global(.p-dark) .self-added-card:hover {
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.25);
}

.medication-details {
  border-top: 1px solid var(--surface-border);
  padding-top: 1rem;
  margin-top: 1rem;
}

/* Enhanced tag styling */
:deep(.p-tag) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  font-weight: 600;
}

/* Section headers */
h4 i {
  font-size: 1.1rem;
}
</style>
