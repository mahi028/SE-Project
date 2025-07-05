<script setup>
import { ref, onMounted } from 'vue'
import { reviewService } from '@/service/ReviewService'
import { useLoginStore } from '@/store/loginStore';

const loginStore = useLoginStore()
const props = defineProps({
    ez_id: {
        type: String,
        required: true
    }
});

const reviews = ref([])
const loading = ref(false)
const showReviewDialog = ref(false)
const submitting = ref(false)

// Review form data
const newReview = ref({
    rating: 0,
    review: ''
})

onMounted(async () => {
  loading.value = true
  try {
    reviews.value = await reviewService.getReviewsByDoctor(props.ez_id)
  } catch (error) {
    console.error('Failed to load user data:', error)
  } finally {
    loading.value = false
  }
})

const getAverageRating = () => {
  return reviewService.getAverageRating(props.ez_id)
}

const getReviewCount = () => {
  return reviewService.getReviewCount(props.ez_id)
}

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
        alert('Please select a rating')
        return
    }

    if (!newReview.value.review.trim()) {
        alert('Please write a review')
        return
    }

    submitting.value = true
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))

        // Add the new review to the list (in a real app, this would be done via API)
        const review = {
            review_id: `R${Date.now()}`,
            sen_id: loginStore.ez_id,
            doc_id: props.ez_id,
            rating: newReview.value.rating,
            review: newReview.value.review
        }

        reviews.value.unshift(review)

        alert('Review submitted successfully!')
        closeReviewDialog()
    } catch (error) {
        console.error('Failed to submit review:', error)
        alert('Failed to submit review. Please try again.')
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
                v-show="loginStore.role === 'senior'"
                label="Write a Review"
                icon="pi pi-plus"
                severity="info"
                outlined
                @click="openReviewDialog"
            />
        </div>

        <div v-if="loading" class="text-center py-6">
        <ProgressSpinner style="width: 60px; height: 60px" strokeWidth="8" />
        </div>

        <div v-else-if="reviews.length === 0" class="text-center py-10">
        <div class="text-gray-500 dark:text-gray-400 mb-3">
            <i class="pi pi-star text-5xl"></i>
        </div>
        <p class="text-gray-600 dark:text-gray-300 text-lg">No reviews available for this doctor yet.</p>
        <p class="text-gray-500 dark:text-gray-400 text-sm mt-2">Be the first to share your experience!</p>
        </div>

        <div v-else class="space-y-4">
        <!-- Reviews Summary -->
        <Card class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 border-l-4 border-blue-500 dark:border-blue-400">
            <template #content>
            <div class="flex items-center gap-4">
                <div class="text-center">
                    <div class="text-4xl font-bold text-blue-600 dark:text-blue-300">{{ getAverageRating() }}</div>
                    <Rating :modelValue="parseFloat(getAverageRating())" readonly :cancel="false" class="text-xl" />
                </div>
                <div>
                    <p class="text-lg font-semibold text-gray-800 dark:text-gray-100">Overall Rating</p>
                    <p class="text-gray-600 dark:text-gray-300">Based on {{ getReviewCount() }} patient reviews</p>
                </div>
            </div>
            </template>
        </Card>

        <!-- Individual Reviews -->
        <div class="grid gap-4">
            <Card v-for="review in reviews" :key="review.review_id" class="shadow-sm hover:shadow-md transition-shadow bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
            <template #content>
                <div class="space-y-3">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                    <Avatar
                        :label="review.sen_id.substring(1)"
                        class="bg-blue-500 dark:bg-blue-600 text-white"
                        shape="circle"
                    />
                    <div>
                        <p class="font-semibold text-gray-800 dark:text-gray-100">Patient {{ review.sen_id }}</p>
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
</style>
