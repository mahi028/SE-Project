<script setup>
import { ref, onMounted, computed } from 'vue'
import { doctorService } from '@/service/DoctorService'
import { appointmentService } from '@/service/AppointmentService'
import { reviewService } from '@/service/ReviewService'
import { useLoginStore } from '@/store/loginStore'
import { useRoute } from 'vue-router'
import InfoItem from '@/components/InfoItem.vue'
import DoctorReviews from '@/components/doctorDashboard/DoctorReviews.vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

const route = useRoute()
const loginStore = useLoginStore()
const toast = useToast()
const confirm = useConfirm()
const userDetails = ref({
  availability: [],
  appointment_window: 30,
  name: '',
  specialization: '',
  hospital: '',
  consultation_fee: '',
  timings: ''
})
const appointments = ref([])
const reviews = ref([])
const loading = ref(false)
const showBookingDialog = ref(false)
const bookingForm = ref({
  date: null,
  time: '',
  reason: ''
})
const availableSlots = ref([])
const loadingSlots = ref(false)
const submittingBooking = ref(false)
const showSuggestionDialog = ref(false)
const submittingSuggestion = ref(false)

// Suggestion form data
const suggestionForm = ref({
  type: '',
  message: ''
})

const suggestionTypes = [
  { label: 'Document Issues', value: 'document' },
  { label: 'Profile Information Missing', value: 'profile' },
  { label: 'Qualification Verification', value: 'qualification' },
  { label: 'Policy Violation', value: 'policy' },
  { label: 'General Feedback', value: 'general' }
]

onMounted(async () => {
  loading.value = true
  try {
    const doctorData = await doctorService.getDoctor({ "ez_id": route.params.ez_id })

    if (doctorData) {
      // Ensure userDetails has proper defaults and is properly structured
      userDetails.value = {
        ...doctorData,
        availability: Array.isArray(doctorData?.availability) ? doctorData.availability : [],
        appointment_window: doctorData?.appointment_window || 30,
        name: doctorData?.name || '',
        specialization: doctorData?.specialization || '',
        hospital: doctorData?.hospital || '',
        consultation_fee: doctorData?.consultation_fee || '',
        timings: doctorData?.timings || ''
      }
    }

    // Only fetch appointments if user is a senior
    if (loginStore.role === 'senior') {
      appointments.value = await appointmentService.getAppointmentsBetweenDoctorAndSenior(
        route.params.ez_id,
        loginStore.ez_id
      )
    }

    reviews.value = await reviewService.getReviewsByDoctor(route.params.ez_id)
  } catch (error) {
    // userDetails already has safe defaults
  } finally {
    loading.value = false
  }
})

const getAverageRating = () => {
  return reviewService.getAverageRating(route.params.ez_id)
}

const getReviewCount = () => {
  return reviewService.getReviewCount(route.params.ez_id)
}

const updateDoctorStatus = async (newStatus) => {
  try {
    const updatedDoctor = await doctorService.updateDoctorStatus(route.params.ez_id, newStatus)
    if (updatedDoctor) {
      userDetails.value.status = newStatus
      // Show success message
    }
  } catch (error) {
  }
}

const getStatusButtonSeverity = (status) => {
  switch (status) {
    case 1:
      return 'success'
    case 0:
      return 'warning'
    case -1:
      return 'danger'
    case -2:
      return 'danger'
    default:
      return 'secondary'
  }
}

const openDocument = (documentType, fileName) => {
  // For now, just show an alert with the document info
  // In a real application, this would open the document in a new tab or modal
  alert(`Opening ${documentType}: ${fileName}`)

  // Future implementation might look like:
  // window.open(`/api/documents/${userDetails.value.ez_id}/${fileName}`, '_blank')
}

const getDocumentIcon = (documentType) => {
  switch (documentType) {
    case 'id_proof':
      return 'pi pi-id-card'
    case 'medical_license':
      return 'pi pi-file-check'
    case 'qualification_cert':
      return 'pi pi-graduation-cap'
    case 'passport_photo':
      return 'pi pi-image'
    default:
      return 'pi pi-file'
  }
}

const getDocumentLabel = (documentType) => {
  switch (documentType) {
    case 'id_proof':
      return 'ID Proof'
    case 'medical_license':
      return 'Medical License'
    case 'qualification_cert':
      return 'Qualification Certificate'
    case 'passport_photo':
      return 'Passport Photo'
    default:
      return 'Document'
  }
}

const openSuggestionDialog = () => {
  suggestionForm.value = {
    type: '',
    message: ''
  }
  showSuggestionDialog.value = true
}

const closeSuggestionDialog = () => {
  showSuggestionDialog.value = false
  suggestionForm.value = {
    type: '',
    message: ''
  }
}

const submitSuggestion = async () => {
  if (!suggestionForm.value.type || !suggestionForm.value.message.trim()) {
    alert('Please fill in all fields')
    return
  }

  submittingSuggestion.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))

    alert('Suggestion/Request has been sent to the doctor successfully!')
    closeSuggestionDialog()
  } catch (error) {
    alert('Failed to send suggestion. Please try again.')
  } finally {
    submittingSuggestion.value = false
  }
}

const isFormValid = () => {
  return suggestionForm.value.type && suggestionForm.value.message.trim().length > 0
}

// Book appointment functionality
const openBookingDialog = () => {
  bookingForm.value = {
    date: null,
    time: '',
    reason: ''
  }
  availableSlots.value = []
  showBookingDialog.value = true
}

const closeBookingDialog = () => {
  showBookingDialog.value = false
  bookingForm.value = {
    date: null,
    time: '',
    reason: ''
  }
  availableSlots.value = []
}

const onDateSelect = async () => {
  if (!bookingForm.value.date) {
    availableSlots.value = []
    return
  }

  loadingSlots.value = true
  try {
    // Ensure date is properly formatted
    let selectedDate
    if (bookingForm.value.date instanceof Date) {
      selectedDate = bookingForm.value.date.toISOString().split('T')[0]
    } else {
      selectedDate = bookingForm.value.date
    }

    availableSlots.value = await appointmentService.getAvailableSlots(route.params.ez_id, selectedDate)
    bookingForm.value.time = '' // Reset time selection
  } catch (error) {
    availableSlots.value = []
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load available time slots',
      life: 3000
    })
  } finally {
    loadingSlots.value = false
  }
}

const bookAppointment = async () => {
  if (!bookingForm.value.date || !bookingForm.value.time || !bookingForm.value.reason.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Missing Information',
      detail: 'Please fill in all required fields',
      life: 3000
    })
    return
  }

  submittingBooking.value = true
  try {
    // Ensure date is properly formatted
    let formattedDate
    if (bookingForm.value.date instanceof Date) {
      formattedDate = bookingForm.value.date.toISOString().split('T')[0]
    } else {
      formattedDate = bookingForm.value.date
    }

    const appointmentData = {
      sen_id: loginStore.ez_id,
      doc_id: route.params.ez_id,
      date: formattedDate,
      time: bookingForm.value.time,
      reason: bookingForm.value.reason.trim()
    }

    await appointmentService.bookAppointment(appointmentData)

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Appointment booked successfully!',
      life: 3000
    })

    closeBookingDialog()

    // Refresh appointments list
    if (loginStore.role === 'senior') {
      appointments.value = await appointmentService.getAppointmentsBetweenDoctorAndSenior(
        route.params.ez_id,
        loginStore.ez_id
      )
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Booking Failed',
      detail: error.message || 'Failed to book appointment. Please try again.',
      life: 3000
    })
  } finally {
    submittingBooking.value = false
  }
}

const getAvailableSlots = () => {
  return availableSlots.value.filter(slot => slot.available)
}

const isBookingFormValid = () => {
  return bookingForm.value.date &&
         bookingForm.value.time &&
         bookingForm.value.reason.trim().length > 0
}

const getMinDate = () => {
  const today = new Date()
  return today
}

const getMaxDate = () => {
  const maxDate = new Date()
  maxDate.setMonth(maxDate.getMonth() + 3) // Allow booking up to 3 months ahead
  return maxDate
}

// Change from function to computed array of disabled dates
const disabledDates = computed(() => {
  const disabled = []
  const today = new Date()
  const maxDate = getMaxDate()

  // Generate dates for the next 3 months
  for (let d = new Date(today); d <= maxDate; d.setDate(d.getDate() + 1)) {
    const checkDate = new Date(d)

    try {
      // Don't allow past dates
      const todayCheck = new Date()
      todayCheck.setHours(0, 0, 0, 0)
      checkDate.setHours(0, 0, 0, 0)

      if (checkDate < todayCheck) {
        disabled.push(new Date(checkDate))
        continue
      }

      // Check if userDetails and availability exist and are valid
      const availability = userDetails.value?.availability

      if (!availability || !Array.isArray(availability) || availability.length === 0) {
        disabled.push(new Date(checkDate))
        continue
      }

      const dayName = checkDate.toLocaleDateString('en-US', { weekday: 'long' })
      const isDisabled = !availability.includes(dayName)

      if (isDisabled) {
        disabled.push(new Date(checkDate))
      }
    } catch (error) {
      disabled.push(new Date(checkDate))
    }
  }

  return disabled
})

// Add computed property for better reactivity
const doctorAvailabilityText = computed(() => {
  const availability = userDetails.value?.availability
  if (!availability || !Array.isArray(availability) || availability.length === 0) {
    return 'Loading availability...'
  }
  return availability.join(', ')
})

// Add computed property to check if booking is available
const canBookAppointment = computed(() => {
  return userDetails.value?.availability &&
         Array.isArray(userDetails.value.availability) &&
         userDetails.value.availability.length > 0 &&
         userDetails.value.status === 1
})

const cancelAppointment = (appointment) => {
  confirm.require({
    message: `Are you sure you want to cancel your appointment with ${userDetails.value.name} on ${appointment.date} at ${appointment.time}?`,
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
        // Simulate API call to cancel appointment
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // Remove appointment from list
        appointments.value = appointments.value.filter(apt => 
          !(apt.doc_id === appointment.doc_id && apt.date === appointment.date && apt.time === appointment.time)
        )
        
        toast.add({
          severity: 'success',
          summary: 'Appointment Cancelled',
          detail: 'Your appointment has been cancelled successfully.',
          life: 3000
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
  const appointmentDateTime = new Date(`${appointment.date} ${appointment.time}`)
  return appointmentDateTime >= new Date()
}
</script>

<template>
  <Toast />
  <ConfirmDialog />
  <div class="p-4 max-w-7xl mx-auto">
    <div v-if="loginStore.role === 'mod' || loginStore.ez_id === userDetails.ez_id">
        <div v-show="userDetails.status === 1"> <h3> Active Doctor Profile! </h3></div>
        <div v-show="userDetails.status === 0"> <h3> Approval Pending! </h3></div>
        <div v-show="userDetails.status === -1"> <h3> The request has been rejected for this doctor! </h3></div>
        <div v-show="userDetails.status === -2"> <h3> Flagged Doctor! </h3></div>
    </div>
    <Card class="w-full">
      <template #content>
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
              <InfoItem type="basic" label="Location" :value="userDetails.address + ', ' + userDetails.pincode" />
              <InfoItem type="basic" label="Specialization" :value="userDetails.specialization || 'N/A'" />
              <div>
                <span class="text-xl font-semibold block mb-2">Reviews</span>
                <div class="flex items-center gap-2">
                  <Rating :modelValue="parseFloat(getAverageRating())" readonly :cancel="false" />
                  <span class="text-lg font-medium">{{ getAverageRating() }}</span>
                  <span class="text-gray-600">({{ getReviewCount() }} reviews)</span>
                </div>
              </div>
              <InfoItem
                type="basic"
                label="Contact"
                :value="userDetails.phone"
                :isLink="true"
                :href="`tel:${userDetails.phone}`"
              />
            </div>
          </div>
        </div>

        <Divider />

        <!-- Professional & Affiliation Info for Doctors -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- Professional Info -->
          <div>
            <h3 class="text-2xl font-semibold mb-4">Professional Information</h3>
            <InfoItem label="Specialization" :value="userDetails.specialization" />
            <InfoItem label="Years of Experience" :value="userDetails.experience" />
            <InfoItem label="Degrees/Qualifications" :value="userDetails.qualification" />
          </div>

          <!-- Affiliation Info -->
          <div>
            <h3 class="text-2xl font-semibold mb-4">Affiliation & Work Details</h3>
            <InfoItem label="Hospital/Clinic" :value="userDetails.hospital" />
            <InfoItem
              label="Official Email"
              :value="userDetails.email"
              :isLink="true"
              :href="`mailto:${userDetails.email}`"
            />
            <InfoItem label="Working Hours" :value="userDetails.timings" />
            <InfoItem
              label="Days Available"
              :value="(userDetails.availability || []).join(', ')"
            />
          </div>
        </div>
        <Divider />

        <!-- Mod Funtionalities -->
        <div v-if="loginStore.role === 'mod'">
            <h3 class="text-2xl font-semibold mb-4 flex items-center gap-2">
                <i class="pi pi-shield text-blue-500"></i>
                Moderator Controls
            </h3>

            <!-- Current Status Display -->
            <div class="mb-6">
                <div class="flex items-center gap-3 mb-4">
                    <span class="text-lg font-medium">Current Status:</span>
                    <Tag
                        :value="userDetails.status === 1 ? 'Approved' :
                               userDetails.status === 0 ? 'Pending' :
                               userDetails.status === -1 ? 'Rejected' :
                               userDetails.status === -2 ? 'Flagged' : 'Unknown'"
                        :severity="getStatusButtonSeverity(userDetails.status)"
                        class="text-lg px-3 py-1"
                    />
                </div>

                <!-- Status Change Buttons -->
                <div class="flex flex-wrap gap-3 mb-4">
                    <!-- Pending approval (status = 0): Show Approve and Reject -->
                    <Button
                        v-if="userDetails.status === 0"
                        label="Approve Doctor"
                        icon="pi pi-check"
                        severity="success"
                        @click="updateDoctorStatus(1)"
                        class="flex-shrink-0"
                    />

                    <Button
                        v-if="userDetails.status === 0"
                        label="Reject Doctor"
                        icon="pi pi-times"
                        severity="danger"
                        @click="updateDoctorStatus(-1)"
                        class="flex-shrink-0"
                    />

                    <!-- Approved (status = 1): Show Flag and Restrict -->
                    <Button
                        v-if="userDetails.status === 1"
                        label="Flag Doctor"
                        icon="pi pi-flag"
                        severity="danger"
                        outlined
                        @click="updateDoctorStatus(-2)"
                        class="flex-shrink-0"
                    />

                    <Button
                        v-if="userDetails.status === 1"
                        label="Restrict Doctor"
                        icon="pi pi-ban"
                        severity="danger"
                        @click="updateDoctorStatus(-1)"
                        class="flex-shrink-0"
                    />

                    <!-- Flagged (status = -2): Show Un-flag and Restrict -->
                    <Button
                        v-if="userDetails.status === -2"
                        label="Un-flag Doctor"
                        icon="pi pi-flag-fill"
                        severity="warning"
                        @click="updateDoctorStatus(1)"
                        class="flex-shrink-0"
                    />

                    <Button
                        v-if="userDetails.status === -2"
                        label="Restrict Doctor"
                        icon="pi pi-ban"
                        severity="danger"
                        @click="updateDoctorStatus(-1)"
                        class="flex-shrink-0"
                    />

                    <!-- Rejected (status = -1): No buttons shown -->
                </div>

                <!-- Suggestion/Request Button for Pending and Flagged Doctors -->
                <div v-if="userDetails.status === 0 || userDetails.status === -2" class="mb-4">
                    <Button
                        label="Send Suggestion/Request to Doctor"
                        icon="pi pi-comment"
                        severity="info"
                        outlined
                        @click="openSuggestionDialog"
                        class="flex-shrink-0"
                    />
                </div>

                <!-- Status Descriptions -->
                <div class="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <h4 class="font-semibold mb-2">Status Descriptions:</h4>
                    <ul class="text-sm space-y-1 text-gray-600 dark:text-gray-300">
                        <li><strong>Approved (1):</strong> Doctor profile is active and visible to patients</li>
                        <li><strong>Pending (0):</strong> Doctor registration is awaiting approval</li>
                        <li><strong>Rejected (-1):</strong> Doctor registration has been denied (no actions available)</li>
                        <li><strong>Flagged (-2):</strong> Doctor profile has been flagged for review</li>
                    </ul>
                </div>
            </div>

            <Divider />
        </div>

        <!-- Document Verification Section -->
        <div v-if="(loginStore.role === 'mod' || loginStore.ez_id === userDetails.ez_id) && userDetails.documents" class="mb-6">
            <h4 class="text-lg font-semibold mb-3 flex items-center gap-2">
                <i class="pi pi-file-check text-green-500"></i>
                {{ loginStore.role === 'mod' ? 'Document Verification' : 'Your Documents' }}
            </h4>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card
                    v-for="(fileName, documentType) in userDetails.documents"
                    :key="documentType"
                    class="cursor-pointer hover:shadow-lg transition-shadow"
                    @click="openDocument(documentType, fileName)"
                >
                    <template #content>
                        <div class="flex items-center gap-3 p-2">
                            <div class="flex-shrink-0">
                                <i :class="getDocumentIcon(documentType)" class="text-2xl text-blue-500"></i>
                            </div>
                            <div class="flex-1">
                                <h5 class="font-semibold text-gray-800 dark:text-gray-200">
                                    {{ getDocumentLabel(documentType) }}
                                </h5>
                                <p class="text-sm text-gray-600 dark:text-gray-400">
                                    {{ fileName }}
                                </p>
                            </div>
                            <div class="flex-shrink-0">
                                <i class="pi pi-external-link text-gray-400"></i>
                            </div>
                        </div>
                    </template>
                </Card>
            </div>

            <div class="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                    <i class="pi pi-info-circle"></i>
                    <span class="text-sm">
                        {{ loginStore.role === 'mod'
                            ? 'Click on any document to view it. Verify all documents before approving the doctor.'
                            : 'Click on any document to view or download it.' }}
                    </span>
                </div>
            </div>

            <Divider />
        </div>

        <!-- Other Informations -->
        <div v-if="userDetails.status === 1">
            <!-- Book Appointment Section (only for seniors) -->
            <div v-if="loginStore.role === 'senior'" class="mb-8">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-2xl font-semibold">Book Appointment</h3>
                    <Button
                        label="Book New Appointment"
                        icon="pi pi-calendar-plus"
                        severity="success"
                        @click="openBookingDialog"
                        :disabled="!canBookAppointment"
                    />
                </div>
                <div class="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-green-700 dark:text-green-300">
                        <i class="pi pi-info-circle"></i>
                        <div class="text-sm">
                            <p class="font-medium mb-1">Appointment Information</p>
                            <ul class="space-y-1">
                                <li>• Consultation Fee: {{ userDetails.consultation_fee || 'Not specified' }}</li>
                                <li>• Appointment Duration: {{ userDetails.appointment_window || 30 }} minutes</li>
                                <li>• Available Days: {{ doctorAvailabilityText }}</li>
                                <li>• Working Hours: {{ userDetails.timings || 'Not specified' }}</li>
                            </ul>
                        </div>
                    </div>
                </div>
                <Divider />
            </div>

            <!-- Show alternative section for non-seniors -->
            <div v-else class="mb-8">
                <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div class="flex items-center gap-2 text-blue-700 dark:text-blue-300">
                        <i class="pi pi-info-circle"></i>
                        <div class="text-sm">
                            <p class="font-medium mb-1">Appointment Booking</p>
                            <p>Only senior citizens can book appointments with doctors.</p>
                            <p class="mt-2">Current user role: <strong>{{ loginStore.role }}</strong></p>
                        </div>
                    </div>
                </div>
                <Divider />
            </div>

            <!-- Appointment History Section -->
            <div class="mt-8" v-if="loginStore.role === 'senior'">
                <h3 class="text-2xl font-semibold mb-6">Your Appointment History with {{ userDetails.name }}</h3>
                <div v-if="loading" class="text-center py-6">
                    <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                </div>
                <div v-else-if="appointments.length === 0" class="text-center py-10">
                    <div class="text-gray-500 mb-3">
                        <i class="pi pi-calendar-times text-5xl"></i>
                    </div>
                    <p class="text-gray-600 text-lg">No appointments found with this doctor.</p>
                    <div class="flex justify-center mt-4">
                        <Button
                            label="Book Your First Appointment"
                            icon="pi pi-calendar-plus"
                            severity="success"
                            @click="openBookingDialog"
                        />
                    </div>
                </div>
                <div v-else>
                    <DataTable
                    :value="appointments"
                    :rows="10"
                    :paginator="appointments.length > 10"
                    responsiveLayout="scroll"
                    class="p-datatable-lg text-base"
                    >
                    <Column field="date" header="Date" sortable style="width: 20%">
                            <template #body="{ data }">
                            <span class="font-semibold text-base">{{ data.date }}</span>
                            </template>
                    </Column>
                    <Column field="time" header="Time" style="width: 15%">
                            <template #body="{ data }">
                            <span class="text-base">{{ data.time }}</span>
                            </template>
                    </Column>
                    <Column field="reason" header="Reason" style="width: 50%">
                            <template #body="{ data }">
                            <span class="text-base">{{ data.reason }}</span>
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
            <Divider />
            <DoctorReviews :ez_id="route.params.ez_id"/>
        </div>
      </template>
    </Card>

    <!-- Moderator Suggestion/Request Dialog -->
    <Dialog
      v-model:visible="showSuggestionDialog"
      modal
      header="Send Suggestion/Request to Doctor"
      :style="{ width: '600px' }"
      :closable="!submittingSuggestion"
      :dismissableMask="!submittingSuggestion"
    >
      <div class="space-y-6">
        <!-- Message Type Selection -->
        <div>
          <label for="messageType" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Suggestion/Request Type *
          </label>
          <Select
            id="messageType"
            v-model="suggestionForm.type"
            :options="suggestionTypes"
            optionLabel="label"
            optionValue="value"
            placeholder="Select suggestion type"
            class="w-full"
          />
        </div>

        <!-- Message Content -->
        <div>
          <label for="messageContent" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Your Message *
          </label>
          <Textarea
            id="messageContent"
            v-model="suggestionForm.message"
            rows="6"
            class="w-full"
            placeholder="Provide specific feedback, request additional information, or suggest changes that need to be made..."
            :maxlength="1000"
          />
          <div class="flex justify-between items-center mt-2">
            <small class="text-gray-500 dark:text-gray-400">
              Be specific about what changes or additional information is needed
            </small>
            <small class="text-gray-500 dark:text-gray-400">
              {{ suggestionForm.message.length }}/1000
            </small>
          </div>
        </div>

        <!-- Context Info -->
        <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div class="flex items-start gap-2">
            <i class="pi pi-info-circle text-blue-500 mt-1"></i>
            <div class="text-sm text-blue-700 dark:text-blue-300">
              <p class="font-medium mb-1">Doctor Status:
                {{ userDetails.status === 0 ? 'Pending Approval' :
                   userDetails.status === -2 ? 'Flagged for Review' : 'Unknown' }}
              </p>
              <p v-if="userDetails.status === 0">
                Send feedback to help the doctor complete their registration or provide missing information.
              </p>
              <p v-if="userDetails.status === -2">
                Communicate issues that need to be addressed or request clarification from the doctor.
              </p>
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
            @click="closeSuggestionDialog"
            :disabled="submittingSuggestion"
          />
          <Button
            label="Send to Doctor"
            icon="pi pi-send"
            severity="info"
            @click="submitSuggestion"
            :loading="submittingSuggestion"
            :disabled="!isFormValid()"
          />
        </div>
      </template>
    </Dialog>

    <!-- Book Appointment Dialog -->
    <Dialog
      v-model:visible="showBookingDialog"
      modal
      header="Book Appointment"
      :style="{ width: '700px' }"
      :closable="!submittingBooking"
      :dismissableMask="!submittingBooking"
      class="booking-dialog"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <i class="pi pi-calendar-plus text-green-500"></i>
          <span class="text-xl font-semibold">Book Appointment with {{ userDetails.name || 'Doctor' }}</span>
        </div>
      </template>

      <div class="space-y-6">
        <!-- Doctor Information Panel -->
        <Panel header="Doctor Information" class="doctor-info-panel">
          <div class="flex items-center gap-4 p-4">
            <Avatar
              :label="userDetails.name?.charAt(0) || 'D'"
              class="bg-green-500 text-white text-xl"
              shape="circle"
              size="xlarge"
            />
            <div class="flex-1">
              <h4 class="text-xl font-semibold text-surface-900 dark:text-surface-0 mb-2">
                {{ userDetails.name || 'Doctor Name' }}
              </h4>
              <p class="text-surface-600 dark:text-surface-400 mb-2">
                {{ userDetails.specialization || 'Specialization' }} • {{ userDetails.hospital || 'Hospital' }}
              </p>
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <strong>Consultation Fee:</strong> {{ userDetails.consultation_fee || 'Not specified' }}
                </div>
                <div>
                  <strong>Duration:</strong> {{ userDetails.appointment_window || 30 }} minutes
                </div>
              </div>
            </div>
          </div>
        </Panel>

        <!-- Date Selection - Only show if availability data is loaded -->
        <div v-if="canBookAppointment" class="field">
          <label for="appointmentDate" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            Select Date *
          </label>
          <Calendar
            id="appointmentDate"
            v-model="bookingForm.date"
            class="w-full"
            :minDate="getMinDate()"
            :maxDate="getMaxDate()"
            :disabledDates="disabledDates"
            @date-select="onDateSelect"
            dateFormat="yy-mm-dd"
            :showIcon="true"
            placeholder="Choose appointment date"
            :manualInput="false"
            :inline="false"
          />
          <small class="text-surface-500 dark:text-surface-400 mt-1 block">
            Available on: {{ doctorAvailabilityText }}
          </small>
        </div>

        <!-- Loading state for availability -->
        <div v-else class="field">
          <div class="flex justify-center items-center py-8">
            <ProgressSpinner style="width: 40px; height: 40px" strokeWidth="4" />
            <span class="ml-3 text-surface-600 dark:text-surface-400">Loading doctor availability...</span>
          </div>
        </div>

        <!-- Time Slot Selection -->
        <div v-if="bookingForm.date" class="field">
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            Select Time Slot *
          </label>

          <div v-if="loadingSlots" class="flex justify-center items-center py-8">
            <ProgressSpinner style="width: 40px; height: 40px" strokeWidth="4" />
            <span class="ml-3 text-surface-600 dark:text-surface-400">Loading available slots...</span>
          </div>

          <div v-else-if="getAvailableSlots().length === 0" class="text-center py-8">
            <i class="pi pi-calendar-times text-4xl text-surface-400 mb-3"></i>
            <p class="text-surface-500 dark:text-surface-400">No available slots for this date</p>
          </div>

          <div v-else class="grid grid-cols-3 gap-3">
            <Button
              v-for="slot in getAvailableSlots()"
              :key="slot.time"
              :label="slot.time"
              :outlined="bookingForm.time !== slot.time"
              :severity="bookingForm.time === slot.time ? 'success' : 'secondary'"
              @click="bookingForm.time = slot.time"
              class="time-slot-btn"
            />
          </div>
        </div>

        <!-- Reason for Visit -->
        <div class="field">
          <label for="appointmentReason" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
            Reason for Visit *
          </label>
          <Textarea
            id="appointmentReason"
            v-model="bookingForm.reason"
            rows="4"
            class="w-full"
            placeholder="Please describe the reason for your visit, symptoms, or concerns..."
            :maxlength="500"
          />
          <div class="flex justify-between items-center mt-2">
            <small class="text-surface-500 dark:text-surface-400">
              Be specific to help the doctor prepare for your visit
            </small>
            <small class="text-surface-500 dark:text-surface-400">
              {{ bookingForm.reason.length }}/500
            </small>
          </div>
        </div>

        <!-- Booking Summary -->
        <div v-if="bookingForm.date && bookingForm.time" class="booking-summary">
          <Panel header="Appointment Summary" class="summary-panel">
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div><strong>Doctor:</strong> {{ userDetails.name || 'Doctor Name' }}</div>
              <div><strong>Date:</strong> {{ bookingForm.date instanceof Date ? bookingForm.date.toLocaleDateString() : bookingForm.date }}</div>
              <div><strong>Time:</strong> {{ bookingForm.time }}</div>
              <div><strong>Duration:</strong> {{ userDetails.appointment_window || 30 }} minutes</div>
              <div><strong>Fee:</strong> {{ userDetails.consultation_fee || 'Not specified' }}</div>
              <div><strong>Hospital:</strong> {{ userDetails.hospital || 'Not specified' }}</div>
            </div>
          </Panel>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end gap-3">
          <Button
            label="Cancel"
            icon="pi pi-times"
            outlined
            @click="closeBookingDialog"
            :disabled="submittingBooking"
          />
          <Button
            label="Book Appointment"
            icon="pi pi-check"
            severity="success"
            @click="bookAppointment"
            :loading="submittingBooking"
            :disabled="!isBookingFormValid()"
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

.booking-dialog :deep(.p-dialog-content) {
  padding: 2rem;
}

.doctor-info-panel :deep(.p-panel-content) {
  padding: 0;
}

.summary-panel :deep(.p-panel-content) {
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 8px;
}

.time-slot-btn {
  min-height: 3rem;
  font-weight: 500;
}

.time-slot-btn:hover {
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.field {
  margin-bottom: 1.5rem;
}

.booking-summary {
  margin-top: 2rem;
}

/* Dark mode enhancements */
:global(.p-dark) .summary-panel :deep(.p-panel-content) {
  background: var(--surface-800);
}
</style>
