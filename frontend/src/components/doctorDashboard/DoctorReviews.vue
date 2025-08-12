<script setup>
import { ref, computed } from 'vue'
import { useLoginStore } from '@/store/loginStore';
import { useMutation } from '@vue/apollo-composable';
import gql from 'graphql-tag';
import { useToast } from 'primevue/usetoast';

const loginStore = useLoginStore()
const toast = useToast()

const props = defineProps({
    reviews: {
        type: Array,
        required: true,
        default: () => []
    },
    doctorName: {
        type: String,
        required: false,
        default: 'this doctor'
    },
    ezId: {
        type: String,
        required: false,
    },
    docId: {
        type: Number,
        required: true
    },
    // Add new prop to check if user has appointments with doctor
    hasAppointments: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['reviewAdded'])

const ADD_REVIEW_MUTATION = gql`
  mutation AddDocReview($docId: Int!, $rating: Int!, $review: String!) {
    addDocReview(docId: $docId, rating: $rating, review: $review) {
      message
      status
    }
  }
`;

const { mutate: addDocReview } = useMutation(ADD_REVIEW_MUTATION);

const showReviewDialog = ref(false)
const submitting = ref(false)

// Review form data
const newReview = ref({
    rating: 0,
    review: ''
})

// Computed properties for review statistics
const getAverageRating = computed(() => {
  if (!props.reviews || props.reviews.length === 0) return '0.0'

  const sum = props.reviews.reduce((acc, review) => acc + (parseFloat(review.rating) || 0), 0)
  return (sum / props.reviews.length).toFixed(1)
})

const getReviewCount = computed(() => {
  return props.reviews?.length || 0
})

// Computed property to check if the user can write a review
const canWriteReview = computed(() => {
    return loginStore.role === 0 && props.hasAppointments
})

const openReviewDialog = () => {
    newReview.value = {
        rating: 0,
        review: ''
    }
    showReviewDialog.value = true
}

const closeReviewDialog = () => {
    showReviewDialog.value = false
    newReview.value = {
        rating: 0,
        review: ''
    }
}

const submitReview = async () => {
    if (newReview.value.rating === 0) {
        toast.add({
            severity: 'warn',
            summary: 'Missing Rating',
            detail: 'Please select a rating',
            life: 3000
        })
        return
    }

    if (!newReview.value.review.trim()) {
        toast.add({
            severity: 'warn',
            summary: 'Missing Review',
            detail: 'Please write a review',
            life: 3000
        })
        return
    }

    submitting.value = true
    try {
        const { data } = await addDocReview({
            docId: props.docId,
            rating: newReview.value.rating,
            review: newReview.value.review.trim()
        })

        const response = data?.addDocReview
        if (response?.status === 200 || response?.status === 201) {
            toast.add({
                severity: 'success',
                summary: 'Success',
                detail: response.message || 'Review submitted successfully!',
                life: 3000
            })
            closeReviewDialog()
            // Emit event to parent to refetch data
            emit('reviewAdded')
        } else {
            toast.add({
                severity: 'error',
                summary: 'Error',
                detail: response?.message || 'Failed to submit review',
                life: 3000
            })
        }
    } catch (error) {
        console.error('Failed to submit review:', error)
        toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Review submitted successfully!',
            life: 3000
        })
        closeReviewDialog()
        emit('reviewAdded')
    } finally {
        submitting.value = false
    }
}

const isFormValid = () => {
    return newReview.value.rating > 0 && newReview.value.review.trim().length > 0
}
</script>
<template>
  <!-- Reviews Section -->
  <div class="mt-8">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-2xl font-semibold flex items-center gap-3 text-gray-900 dark:text-gray-100">
        <i class="pi pi-star-fill text-yellow-500"></i>
        Patient Reviews & Ratings
      </h3>
      <Button
        v-show="canWriteReview"
        label="Write a Review"
        icon="pi pi-plus"
        severity="info"
        outlined
        @click="openReviewDialog"
      />
    </div>

    <!-- Show message if senior has no appointments -->
    <div v-if="loginStore.role === 0 && !hasAppointments" class="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
      <div class="flex items-center gap-2 text-yellow-700 dark:text-yellow-300">
        <i class="pi pi-info-circle"></i>
        <span class="text-sm">
          You can only write a review after having an appointment with {{ doctorName }}.
        </span>
      </div>
    </div>

    <div v-if="reviews.length === 0" class="text-center py-10">
      <div class="text-gray-500 dark:text-gray-400 mb-3">
        <i class="pi pi-star text-5xl"></i>
      </div>
      <p class="text-gray-600 dark:text-gray-300 text-lg">No reviews available for {{ doctorName }} yet.</p>
      <p class="text-gray-500 dark:text-gray-400 text-sm mt-2">Be the first to share your experience!</p>
    </div>

    <div v-else class="space-y-4">
      <!-- Reviews Summary -->
      <Card class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-l-4 border-blue-500 dark:border-blue-400">
        <template #content>
          <div class="flex items-center gap-4">
            <div class="text-center">
              <div class="text-4xl font-bold text-blue-600 dark:text-blue-300">{{ getAverageRating }}</div>
              <Rating :modelValue="parseFloat(getAverageRating)" readonly :cancel="false" class="text-xl" />
            </div>
            <div>
              <p class="text-lg font-semibold text-gray-800 dark:text-gray-100">Overall Rating</p>
              <p class="text-gray-600 dark:text-gray-300">Based on {{ getReviewCount }} patient reviews</p>
            </div>
          </div>
        </template>
      </Card>

      <!-- Individual Reviews -->
      <div class="grid gap-4">
        <Card v-for="review in reviews" :key="review.reviewId" class="shadow-sm hover:shadow-md transition-shadow bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <template #content>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <Avatar
                    :label="String(review.senId).padStart(2, '0')"
                    class="bg-blue-500 dark:bg-blue-600 text-white"
                    shape="circle"
                  />
                  <div>
                    <p class="font-semibold text-gray-800 dark:text-gray-100">Patient #{{ review.senId }}</p>
                    <Rating :modelValue="review.rating" readonly :cancel="false" class="text-sm" />
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <Tag
                    :value="`${review.rating}/5`"
                    :severity="review.rating >= 4 ? 'success' : review.rating >= 3 ? 'warning' : 'danger'"
                    class="font-bold"
                  />
                </div>
              </div>

              <div class="pl-12">
                <p class="text-gray-700 dark:text-gray-200 leading-relaxed">{{ review.review }}</p>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>

  <!-- Review Dialog -->
  <Dialog
    v-model:visible="showReviewDialog"
    modal
    header="Write a Review"
    :style="{ width: '500px' }"
    :closable="!submitting"
    :dismissableMask="!submitting"
  >
    <div class="space-y-6">
      <!-- Rating Section -->
      <div class="text-center">
        <label class="block text-lg font-medium text-gray-700 dark:text-gray-300 mb-3">
          Rate your experience
        </label>
        <Rating
          v-model="newReview.rating"
          :cancel="false"
          class="text-2xl justify-center"
        />
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
          {{ newReview.rating === 0 ? 'Please select a rating' :
             newReview.rating === 1 ? 'Poor' :
             newReview.rating === 2 ? 'Fair' :
             newReview.rating === 3 ? 'Good' :
             newReview.rating === 4 ? 'Very Good' : 'Excellent' }}
        </p>
      </div>

      <!-- Review Text Section -->
      <div>
        <label for="reviewText" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Share your experience *
        </label>
        <Textarea
          id="reviewText"
          v-model="newReview.review"
          rows="4"
          class="w-full"
          placeholder="Tell others about your experience with this doctor..."
          :maxlength="500"
        />
        <div class="flex justify-between items-center mt-2">
          <small class="text-gray-500 dark:text-gray-400">
            Be specific and helpful in your review
          </small>
          <small class="text-gray-500 dark:text-gray-400">
            {{ newReview.review.length }}/500
          </small>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <Button
          label="Cancel"
          icon="pi pi-times"
          outlined
          @click="closeReviewDialog"
          :disabled="submitting"
        />
        <Button
          label="Submit Review"
          icon="pi pi-check"
          severity="info"
          @click="submitReview"
          :loading="submitting"
          :disabled="!isFormValid()"
        />
      </div>
    </template>
  </Dialog>
</template>
<style>
a:hover {
  opacity: 0.8;
}
a:hover {
  opacity: 0.8;
}
</style>
