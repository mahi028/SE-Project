<script setup>
function smoothScroll(id) {
    document.body.click(); // closes mobile menu if open
    const element = document.getElementById(id);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
</script>

<template>
    <!-- Logo and Brand -->
    <a class="flex items-center cursor-pointer" href="#">
        <svg viewBox="0 0 54 40" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-12 mr-2">
            <circle cx="27" cy="20" r="18" fill="var(--primary-color)" />
        </svg>
        <span class="text-surface-900 dark:text-surface-0 font-semibold text-2xl leading-normal mr-20">EZCare</span>
    </a>

    <!-- Mobile Menu Toggle -->
    <Button
        class="lg:!hidden"
        text
        severity="secondary"
        rounded
        v-styleclass="{
            selector: '@next',
            enterFromClass: 'hidden',
            enterActiveClass: 'animate-scalein',
            leaveToClass: 'hidden',
            leaveActiveClass: 'animate-fadeout',
            hideOnOutsideClick: true
        }"
    >
        <i class="pi pi-bars !text-2xl"></i>
    </Button>

    <!-- Navigation -->
    <div class="items-center bg-surface-0 dark:bg-surface-900 grow justify-between hidden lg:flex absolute lg:static w-full left-0 top-full px-12 lg:px-0 z-20 rounded-border">
        <ul class="list-none p-0 m-0 flex lg:items-center select-none flex-col lg:flex-row cursor-pointer gap-8">
            <li><a @click="smoothScroll('hero')" class="px-0 py-4 text-surface-900 dark:text-surface-0 font-medium text-xl">Home</a></li>
            <li><a @click="smoothScroll('features')" class="px-0 py-4 text-surface-900 dark:text-surface-0 font-medium text-xl">Features</a></li>
            <li><a @click="smoothScroll('highlights')" class="px-0 py-4 text-surface-900 dark:text-surface-0 font-medium text-xl">Highlights</a></li>
            <li><a @click="smoothScroll('pricing')" class="px-0 py-4 text-surface-900 dark:text-surface-0 font-medium text-xl">Plans</a></li>
        </ul>

        <!-- Auth Buttons -->
        <div class="flex border-t lg:border-t-0 border-surface py-4 lg:py-0 mt-4 lg:mt-0 gap-2">
            <Button label="Login" text as="router-link" to="/auth/login" rounded />
            <Button label="Register" to="/auth/register" rounded />
        </div>
    </div>
</template>
