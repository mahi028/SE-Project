<template>
    <div
        id="hero"
        class="flex flex-col pt-6 px-6 lg:px-20 overflow-hidden"
        style="background: linear-gradient(0deg, rgba(5, 22, 52, 0.2), rgba(15, 92, 88, 0.2)), radial-gradient(77.36% 256.97% at 77.36% 57.52%, #eeeFAF 0%, #c3e3fa 100%)"
    >
        <div class="mx-6 md:mx-20 mt-0 md:mt-6">
            <h1 class="text-6xl font-bold text-gray-900 leading-tight">
                <span class="font-light block">Your Care,</span>
                Just a Tap Away
            </h1>
            <p class="font-normal text-2xl leading-normal md:mt-4 text-gray-700">
                Connect with doctors, get reminders, and find emergency help — all designed for senior ease and comfort.
            </p>
            <Button label="Explore Features" as="router-link" to="/features" rounded class="!text-xl mt-8 !px-4" />
        </div>
        <div class="flex justify-center md:justify-end">
            <img src="#" alt="Hero Image" class="w-9/12 md:w-auto" />
        </div>
    </div>
</template>
