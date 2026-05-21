import { Users, Shield, UserCheck, Plus } from "lucide-react";

const teamMembers = [
  { name: "Ahmed Benali", email: "ahmed.benali@example.dz", role: "Owner", permissions: "Full Access", status: "active", avatar: "AB" },
  { name: "Fatima Zohra", email: "fatima.zohra@example.dz", role: "Manager", permissions: "Manage Products, View Reports", status: "active", avatar: "FZ" },
  { name: "Karim Mansour", email: "karim.mansour@example.dz", role: "Warehouse Staff", permissions: "View Inventory, Process Orders", status: "active", avatar: "KM" },
  { name: "Amina Lounis", email: "amina.lounis@example.dz", role: "Analyst", permissions: "View All, Generate Reports", status: "active", avatar: "AL" },
];

const roles = [
  { name: "Owner", members: 1, description: "Full system access and billing management" },
  { name: "Manager", members: 1, description: "Manage products, inventory, and orders" },
  { name: "Warehouse Staff", members: 1, description: "Process orders and update stock levels" },
  { name: "Analyst", members: 1, description: "View data and generate reports" },
];

export function TeamRoles() {
  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Team & Roles</h1>
          <p className="text-gray-600 mt-1">Manage team members and permissions</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors">
          <Plus className="w-5 h-5" />
          Invite Member
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-indigo-50 rounded-lg">
              <Users className="w-5 h-5 text-indigo-600" />
            </div>
            <p className="text-sm text-gray-600">Team Members</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">4</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-emerald-50 rounded-lg">
              <Shield className="w-5 h-5 text-emerald-600" />
            </div>
            <p className="text-sm text-gray-600">Active Roles</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">4</p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <UserCheck className="w-5 h-5 text-blue-600" />
            </div>
            <p className="text-sm text-gray-600">Pending Invites</p>
          </div>
          <p className="text-3xl font-bold text-gray-900">0</p>
        </div>
      </div>

      {/* Team Members */}
      <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden mb-8">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Team Members</h2>
        </div>
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Member</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Role</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Permissions</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Status</th>
              <th className="text-left py-4 px-6 text-sm font-semibold text-gray-900">Actions</th>
            </tr>
          </thead>
          <tbody>
            {teamMembers.map((member, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-4 px-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-indigo-600">{member.avatar}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{member.name}</p>
                      <p className="text-sm text-gray-500">{member.email}</p>
                    </div>
                  </div>
                </td>
                <td className="py-4 px-6">
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-sm font-medium rounded-full">
                    {member.role}
                  </span>
                </td>
                <td className="py-4 px-6 text-gray-600">{member.permissions}</td>
                <td className="py-4 px-6">
                  <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-medium rounded-full capitalize">
                    {member.status}
                  </span>
                </td>
                <td className="py-4 px-6">
                  <button className="text-sm text-indigo-600 font-medium hover:text-indigo-700">
                    Edit
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Roles */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Roles</h2>
        <div className="grid grid-cols-2 gap-6">
          {roles.map((role, index) => (
            <div key={index} className="border border-gray-200 rounded-xl p-6 hover:border-indigo-300 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-bold text-gray-900">{role.name}</h3>
                <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm font-medium rounded-full">
                  {role.members} {role.members === 1 ? "member" : "members"}
                </span>
              </div>
              <p className="text-sm text-gray-600">{role.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
