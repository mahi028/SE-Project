export const peerGroups = {
  getpeerGroupsData() {
    return [
      { group_id: '1', label: "Exercise Club", day: "Daily", time: "5:00 PM", location: "Shanti Niketan Park", pincode: '201011' },
      { group_id: '2', label: "Let's Talk", day: "Sunday", time: "10:00 AM", location: "Surya Niketan Park", pincode: '201011' },
      { group_id: '3', label: "Walker's Club", day: "Daily", time: "7:00 AM", location: "Bahubali Park", pincode: '201011' },
      { group_id: '4', label: "Comedy Club", day: "Sunday", time: "7:00 PM", location: "Shanti Niketan Park", pincode: '201011' },
      { group_id: '5', label: "Yoga Club", day: "Daily", time: "6:00 AM", location: "Dhruv Park", pincode: '201010' },
      { group_id: '6', label: "Debate Club", day: "Sunday", time: "10:00 AM", location: "Community Hall", pincode: '201010' },
      { group_id: '7', label: "Laughter Club", day: "Sunday", time: "7:00 AM", location: "Community Hall", pincode: '201010' },
      { group_id: '8', label: "Jogging Club", day: "Daily", time: "7:00 AM", location: "Yamuna Sports Complex", pincode: '201010' },
      { group_id: '9', label: "Book Reading Club", day: "Saturday", time: "4:00 PM", location: "Central Library", pincode: '201011' },
      { group_id: '10', label: "Meditation Group", day: "Weekdays", time: "8:00 AM", location: "Peace Garden", pincode: '201011' },
      { group_id: '11', label: "Chess Club", day: "Tuesday", time: "3:00 PM", location: "Community Center", pincode: '201010' },
      { group_id: '12', label: "Dance Group", day: "Friday", time: "6:00 PM", location: "Cultural Hall", pincode: '201010' },
      { group_id: '13', label: "Gardening Club", day: "Wednesday", time: "9:00 AM", location: "Botanical Garden", pincode: '201011' },
      { group_id: '14', label: "Photography Walk", day: "Weekends", time: "7:00 AM", location: "Heritage Park", pincode: '201010' },
      { group_id: '15', label: "Music Circle", day: "Thursday", time: "5:30 PM", location: "Music Academy", pincode: '201011' }
    ];
  },

  getPeerGroups(pincode) {
    return Promise.resolve(
      this.getpeerGroupsData().filter(group => group.pincode === pincode)
    );
  },

  createPeerGroup(groupData) {
    // Simulate creating a new group
    const newGroup = {
      group_id: Date.now().toString(),
      ...groupData
    };
    return Promise.resolve(newGroup);
  },

  joinPeerGroup(groupId, userId) {
    // Simulate joining a group
    return Promise.resolve({
      success: true,
      message: 'Successfully joined the group'
    });
  }
};
