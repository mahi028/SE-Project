<script setup>
import { ref, onMounted, computed } from 'vue'
import { useLazyQuery, useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';
import { useLoginStore } from '@/store/loginStore'
import { useRoute, useRouter } from 'vue-router'
import InfoItem from '@/components/InfoItem.vue'
import DoctorReviews from '@/components/doctorDashboard/DoctorReviews.vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

const route = useRoute()
const router = useRouter()
const loginStore = useLoginStore()
const toast = useToast()
const confirm = useConfirm()

// Add missing reactive variables for dialogs and forms
const showSuggestionDialog = ref(false)
const showBookingDialog = ref(false)
const suggestionForm = ref({
  type: '',
  message: ''
})
const bookingForm = ref({
  date: null,
  time: '',
  reason: ''
})
const availableSlots = ref([])
const loadingSlots = ref(false)
const submittingBooking = ref(false)
const submittingSuggestion = ref(false)

const suggestionTypes = [
  { label: 'Document Issues', value: 'document' },
  { label: 'Profile Information Missing', value: 'profile' },
  { label: 'Qualification Verification', value: 'qualification' },
  { label: 'Policy Violation', value: 'policy' },
  { label: 'General Feedback', value: 'general' }
]

const GET_DOCTOR_DATA = gql`
  query GetUser($ezId: String!) {
    getUser(ezId: $ezId) {
      ezId
      role
      email
      createdAt
      name
      phoneNum
      profileImageUrl
      docInfo {
        docId
        ezId
        gender
        dob
        address
        pincode
        alternatePhoneNum
        licenseNumber
        specialization
        affiliation
        qualification
        experience
        consultationFee
        workingHours
        availability
        reviews
        availabilityStatus
        documents
        appointmentWindow
        docReviews {
          reviewId
          docId
          senId
          rating
          review
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

const GET_AVAILABLE_SLOTS = gql`
    query GetAvailableSlots($docId: Int!, $date: String!) {
        getAvailableSlots(docId: $docId, date: $date) {
            slots
        }
    }
`;

const { load: fetchDoctor, result, loading: userLoading, error } = useLazyQuery(GET_DOCTOR_DATA)
const { load: fetchAppointments, result: appointmentsResult, loading: appointmentsLoading } = useLazyQuery(GET_APPOINTMENTS)
const { load: fetchAvailableSlots, result: slotsResult, loading: slotsLoading } = useLazyQuery(GET_AVAILABLE_SLOTS)

// Add new ref for role mismatch dialog
const showRoleMismatchDialog = ref(false)
const foundUser = ref(null)

// Computed properties to extract data from GraphQL result
const userDetails = computed(() => {
  const user = result.value?.getUser
  const docInfo = user?.docInfo
  if (!user) return null

  // Check if user role matches expected role (1 for doctor)
  if (user.role !== 1) {
    foundUser.value = user
    showRoleMismatchDialog.value = true
    return null
  }

  if (!docInfo) return null // Return null instead of default object

  // Parse affiliation if it's JSON string
  let affiliationData = {}
  try {
    affiliationData = typeof docInfo.affiliation === 'string'
      ? JSON.parse(docInfo.affiliation)
      : (docInfo.affiliation || {})
  } catch (e) {
    console.error('Error parsing affiliation:', e)
  }

  // Parse availability if it's JSON string
  let availabilityArray = []
  try {
    availabilityArray = typeof docInfo.availability === 'string'
      ? JSON.parse(docInfo.availability)
      : (Array.isArray(docInfo.availability) ? docInfo.availability : [])
  } catch (e) {
    console.error('Error parsing availability:', e)
  }

  return {
    name: user.name,
    email: user.email,
    ezId: user.ezId,
    phone: user.phoneNum,
    alternatePhone: docInfo.alternatePhoneNum,
    address: docInfo.address,
    pincode: docInfo.pincode,
    specialization: docInfo.specialization,
    licenseNumber: docInfo.licenseNumber,
    experience: docInfo.experience ? String(docInfo.experience) : 'Not specified',
    consultation_fee: docInfo.consultationFee ? String(docInfo.consultationFee) : 'Not specified',
    qualification: typeof docInfo.qualification === 'string' ? JSON.parse(docInfo.qualification) : docInfo.qualification,
    hospital: affiliationData.name || 'Not specified',
    timings: docInfo.workingHours || 'Not specified',
    availability: availabilityArray,
    appointment_window: docInfo.appointmentWindow || 30,
    status: docInfo.availabilityStatus || 0,
    documents: typeof docInfo.documents === 'string' ? JSON.parse(docInfo.documents) : docInfo.documents,
    profileImageUrl: user.profileImageUrl
  }
})

const appointments = computed(() => {
  return appointmentsResult.value?.getAppointmentsForDoctorSenior || []
})

const reviews = computed(() => {
  return result.value?.getUser?.docInfo?.docReviews || []
})

const getAverageRating = () => {
  const reviewList = reviews.value
  if (!reviewList || reviewList.length === 0) return '0.0'

  const sum = reviewList.reduce((acc, review) => acc + (parseFloat(review.rating) || 0), 0)
  return (sum / reviewList.length).toFixed(1)
}

const getReviewCount = () => {
  return reviews.value?.length || 0
}

const updateDoctorStatus = async (newStatus) => {
  try {
    const updatedDoctor = await doctorService.updateDoctorStatus(route.params.ezId, newStatus)
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
  // window.open(`/api/documents/${userDetails.value.ezId}/${fileName}`, '_blank')
}

const getDocumentIcon = (documentType) => {
  switch (documentType) {
    case 'idProof':
      return 'pi pi-id-card'
    case 'licenseCert':
      return 'pi pi-file-check'
    case 'qualificationCerts':
      return 'pi pi-graduation-cap'
    case 'passportPhoto':
      return 'pi pi-image'
    default:
      return 'pi pi-file'
  }
}

const getDocumentLabel = (documentType) => {
  switch (documentType) {
    case 'idProof':
      return 'ID Proof'
    case 'licenseCert':
      return 'Medical License'
    case 'qualificationCerts':
      return 'Qualification Certificate'
    case 'passportPhoto':
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

const BOOK_APPOINTMENT = gql`
    mutation BookAppointment($docId: Int!, $reason: String!, $remTime: DateTime!) {
        bookAppointment(docId: $docId, reason: $reason, remTime: $remTime) {
            message
            status
        }
    }
`;

const CANCEL_APPOINTMENT = gql`
    mutation CancelAppointment($appId: Int!) {
        cancelAppointment(appId: $appId) {
            message
            status
        }
    }
`;

const { mutate: bookAppointmentMutation } = useMutation(BOOK_APPOINTMENT);
const { mutate: cancelAppointmentMutation } = useMutation(CANCEL_APPOINTMENT);

const onDateSelect = async () => {
    if (!bookingForm.value.date) {
        availableSlots.value = []
        return
    }

    loadingSlots.value = true
    try {
        // Format date for the GraphQL query (DD-MM-YYYY format)
        let formattedDate
        if (bookingForm.value.date instanceof Date) {
            const day = bookingForm.value.date.getDate().toString()
            const month = (bookingForm.value.date.getMonth() + 1).toString()
            const year = bookingForm.value.date.getFullYear().toString()
            formattedDate = `${day}-${month}-${year}`
        } else {
            // If date is already a string, parse it first
            const dateObj = new Date(bookingForm.value.date)
            const day = dateObj.getDate().toString()
            const month = (dateObj.getMonth() + 1).toString()
            const year = dateObj.getFullYear().toString()
            formattedDate = `${day}-${month}-${year}`
        }

        // Use the actual docId from the doctor's info instead of parsing ezId
        const docId = result.value?.getUser?.docInfo?.docId
        if (!docId) {
            console.error('Doctor ID not found')
            availableSlots.value = []
            return
        }

        // console.log('Fetching slots for docId:', docId, 'date:', formattedDate)

        await fetchAvailableSlots(GET_AVAILABLE_SLOTS, {
            docId: docId,
            date: formattedDate
        })

        const slots = slotsResult.value?.getAvailableSlots?.slots || []

        // Transform slots to match expected format
        availableSlots.value = slots.map(slot => ({
            time: slot,
            available: true
        }))

        bookingForm.value.time = '' // Reset time selection
    } catch (error) {
        console.error('Error fetching available slots:', error)
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
        // Convert date and time to proper DateTime format
        let appointmentDateTime
        if (bookingForm.value.date instanceof Date) {
            appointmentDateTime = new Date(bookingForm.value.date)
        } else {
            appointmentDateTime = new Date(bookingForm.value.date)
        }

        // Parse time and set on the date
        const [time, period] = bookingForm.value.time.split(' ')
        const [hours, minutes] = time.split(':')
        let hour24 = parseInt(hours)

        if (period === 'PM' && hour24 !== 12) {
            hour24 += 12
        } else if (period === 'AM' && hour24 === 12) {
            hour24 = 0
        }

        appointmentDateTime.setHours(hour24, parseInt(minutes), 0, 0)

        // Use the actual docId from the doctor's info
        const docId = result.value?.getUser?.docInfo?.docId
        if (!docId) {
            console.error('Doctor ID not found')
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: 'Doctor information not available',
                life: 3000
            })
            return
        }

        const { data } = await bookAppointmentMutation({
            docId: docId,
            reason: bookingForm.value.reason.trim(),
            remTime: appointmentDateTime.toISOString()
        })

        const response = data?.bookAppointment

        if (response?.status === 201) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: response.message || 'Appointment booked successfully!',
                life: 3000
            })

            closeBookingDialog()

            // Refetch appointments list if senior is viewing
            if (loginStore.role === 0) {
                await fetchAppointments(GET_APPOINTMENTS, {
                    senId: loginStore.ezId,
                    docId: route.params.ezId
                })
            }
        } else {
            toast.add({
                severity: 'error',
                summary: 'Booking Failed',
                detail: response?.message || 'Failed to book appointment. Please try again.',
                life: 3000
            })
        }
    } catch (error) {
        console.error('Error booking appointment:', error)
        toast.add({
            severity: 'error',
            summary: 'Booking Failed',
            detail: 'Failed to book appointment. Please try again.',
            life: 3000
        })
    } finally {
        submittingBooking.value = false
    }
}

const cancelAppointment = (appointment) => {
  confirm.require({
    message: `Are you sure you want to cancel your appointment with ${userDetails.value.name} on ${new Date(appointment.remTime).toLocaleDateString()}?`,
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
        const { data } = await cancelAppointmentMutation({
          appId: appointment.appId
        })

        const response = data?.cancelAppointment

        if (response?.status === 1) {
          toast.add({
            severity: 'success',
            summary: 'Appointment Cancelled',
            detail: response.message || 'Your appointment has been cancelled successfully.',
            life: 3000
          })

          // Refetch appointments
          if (loginStore.role === 0) {
            await fetchAppointments(GET_APPOINTMENTS, {
              senId: loginStore.ezId,
              docId: route.params.ezId
            })
          }
        } else {
          toast.add({
            severity: 'error',
            summary: 'Error',
            detail: response?.message || 'Failed to cancel appointment. Please try again.',
            life: 3000
          })
        }
      } catch (error) {
        console.error('Error cancelling appointment:', error)
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

// Add function to handle review added event
const handleReviewAdded = async () => {
  // Refetch doctor data to get updated reviews
  try {
    await fetchDoctor({ ezId: route.params.ezId })
  } catch (error) {
    console.error('Failed to refetch doctor data:', error)
  }
}

// Add computed property to check if current user has appointments with this doctor
const hasAppointments = computed(() => {
  return appointments.value.length > 0
})

// Redirect to correct profile based on user role
const redirectToCorrectProfile = () => {
  if (foundUser.value) {
    const correctRoute = foundUser.value.role === 0 ? '/senior/' : '/doctor/'
    router.push(correctRoute + foundUser.value.ezId)
  }
  showRoleMismatchDialog.value = false
}

const closeRoleMismatchDialog = () => {
  showRoleMismatchDialog.value = false
  foundUser.value = null
}

// Add missing computed properties
const doctorAvailabilityText = computed(() => {
  const availability = userDetails.value?.availability
  if (!availability || !Array.isArray(availability) || availability.length === 0) {
    return 'Not specified'
  }
  return availability.join(', ')
})

const canBookAppointment = computed(() => {
  return userDetails.value?.availability &&
         Array.isArray(userDetails.value.availability) &&
         userDetails.value.availability.length > 0 &&
         userDetails.value.status === 1
})

const getAvailableSlots = () => {
  return availableSlots.value.filter(slot => slot.available)
}

const getMinDate = () => {
  const today = new Date()
  return today
}

const getMaxDate = () => {
  const maxDate = new Date()
  maxDate.setMonth(maxDate.getMonth() + 3)
  return maxDate
}

const disabledDates = computed(() => {
  const disabled = []
  const today = new Date()
  const maxDate = getMaxDate()

  for (let d = new Date(today); d <= maxDate; d.setDate(d.getDate() + 1)) {
    const checkDate = new Date(d)

    try {
      const todayCheck = new Date()
      todayCheck.setHours(0, 0, 0, 0)
      checkDate.setHours(0, 0, 0, 0)

      if (checkDate < todayCheck) {
        disabled.push(new Date(checkDate))
        continue
      }

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

const isUpcomingAppointment = (appointment) => {
  return new Date(appointment.remTime) >= new Date()
}

const isBookingFormValid = () => {
  return bookingForm.value.date &&
         bookingForm.value.time &&
         bookingForm.value.reason.trim().length > 0
}

// Fix onMounted to properly load data
onMounted(async () => {
  try {
    // console.log('Loading doctor profile for ezId:', route.params.ezId)
    await fetchDoctor(GET_DOCTOR_DATA, { ezId: route.params.ezId })
    // console.log('Doctor data loaded:', result.value?.getUser)

    // Fetch appointments based on user role
    if (loginStore.role === 0) {
      // Senior viewing doctor profile - get appointments between them
      await fetchAppointments(GET_APPOINTMENTS, {
        senId: loginStore.ezId,
        docId: route.params.ezId
      })
    } else if (loginStore.role === 1 && loginStore.ezId === route.params.ezId) {
      // Doctor viewing their own profile - get all their appointments
      await fetchAppointments(GET_APPOINTMENTS, {
        senId: null,
        docId: loginStore.ezId
      })
    }
  } catch (error) {
    console.error('Failed to load doctor data:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load profile data',
      life: 3000
    })
  }
})
</script>

<template>
  <Toast />
  <ConfirmDialog />
  <div class="p-4 max-w-7xl mx-auto">
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
      <h2 class="text-2xl font-bold text-gray-700 dark:text-gray-300 mb-2">Doctor Not Found</h2>
      <p class="text-gray-600 dark:text-gray-400">The doctor profile you're looking for could not be found.</p>
      <p class="text-gray-500 dark:text-gray-500 text-sm mt-2">The doctor may not exist, may not have completed registration, or you may not have permission to view this profile.</p>
    </div>

    <!-- Profile content -->
    <div v-else-if="userDetails">
      <!-- Status indicators for mod/owner -->
      <div v-if="loginStore.role === 'mod' || loginStore.ezId === userDetails.ezId">
          <div v-show="loginStore.ezId === userDetails.ezId" style="text-align: center;"> <h3> Your Profile </h3></div>

        <div v-show="userDetails.status === 1"> <h5> Active Doctor Profile! </h5></div>
        <div v-show="userDetails.status === 0"> <h5> Approval Pending! </h5></div>
        <div v-show="userDetails.status === -1"> <h5> The request has been rejected for this doctor! </h5></div>
        <div v-show="userDetails.status === -2"> <h5> Flagged Doctor! </h5></div>
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
                <InfoItem
                  type="basic"
                  label="Location"
                  :value="userDetails.address ? `${userDetails.address}, ${userDetails.pincode}` : 'Not provided'"
                />
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
                  label="Primary Contact"
                  :value="userDetails.phone"
                  :isLink="true"
                  :href="`tel:${userDetails.phone}`"
                />
                <InfoItem
                  type="basic"
                  label="Alternate Contact"
                  :value="userDetails.alternatePhone || 'Not provided'"
                  :isLink="userDetails.alternatePhone ? true : false"
                  :href="userDetails.alternatePhone ? `tel:${userDetails.alternatePhone}` : null"
                />
              </div>
            </div>
          </div>

          <Divider />

          <!-- Professional & Affiliation Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Professional Info -->
            <div>
              <h3 class="text-2xl font-semibold mb-4">Professional Information</h3>
              <InfoItem label="License Number" :value="userDetails.licenseNumber || 'Not specified'" />
              <InfoItem label="Specialization" :value="userDetails.specialization || 'Not specified'" />
              <InfoItem label="Years of Experience" :value="userDetails.experience" />
              <InfoItem label="Consultation Fee" :value="userDetails.consultation_fee" />
              <InfoItem
                label="Qualifications"
                :value="Array.isArray(userDetails.qualification)
                  ? userDetails.qualification.map(q => `${q.name} (${q.year})`).join(', ')
                  : 'Not specified'"
              />
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
              <InfoItem label="Days Available" :value="doctorAvailabilityText" />
              <InfoItem label="Appointment Window" :value="`${userDetails.appointment_window} minutes`" />
            </div>
          </div>

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
          <div v-if="(loginStore.role === 'mod' || loginStore.ezId === userDetails.ezId) && userDetails.documents" class="mb-6">
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
              <div v-if="loginStore.role === 0" class="mb-8">
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
              <div class="mt-8" v-if="loginStore.role === 0 || (loginStore.role === 1 && loginStore.ezId === route.params.ezId)">
                <h3 class="text-2xl font-semibold mb-6">
                  {{ loginStore.role === 0 ? `Your Appointment History with ${userDetails.name}` : 'Your Appointments' }}
                </h3>
                <div v-if="appointmentsLoading" class="text-center py-6">
                  <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
                </div>
                <div v-else-if="appointments.length === 0" class="text-center py-10">
                  <div class="text-gray-500 mb-3">
                    <i class="pi pi-calendar-times text-5xl"></i>
                  </div>
                  <p class="text-gray-600 text-lg">
                    {{ loginStore.role === 0 ? 'No appointments found with this doctor.' : 'No appointments found.' }}
                  </p>
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
                          v-if="isUpcomingAppointment(data) && loginStore.role === 0"
                          icon="pi pi-times"
                          size="small"
                          severity="danger"
                          outlined
                          @click="cancelAppointment(data)"
                          v-tooltip.top="'Cancel Appointment'"
                        />
                        <span v-else class="text-surface-500 text-sm">
                          {{ isUpcomingAppointment(data) ? 'Upcoming' : 'Completed' }}
                        </span>
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </div>
              <Divider />
              <DoctorReviews
                :reviews="reviews"
                :doctorName="userDetails.name"
                :docId="userDetails.ezId"
                :hasAppointments="hasAppointments"
                @reviewAdded="handleReviewAdded"
              />
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

          <!-- Date Selection -->
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
              <small class="text-surface-400 mt-2 block">
                This doctor may be fully booked or unavailable on this date.
              </small>
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
              <strong>{{ foundUser?.role === 0 ? 'Senior Citizen' : 'User' }}</strong>,
              not a Doctor.
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
    </div>
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
