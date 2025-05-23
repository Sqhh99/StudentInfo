/**
 * 课程表单验证
 */
document.addEventListener('DOMContentLoaded', function() {
    // 获取添加课程表单元素
    const addCourseForm = document.getElementById('addCourseForm');
    
    if (addCourseForm) {
        // 为表单添加提交事件监听器
        addCourseForm.addEventListener('submit', function(event) {
            // 标记表单是否有效
            let isValid = true;
            
            // 获取必填字段
            const code = document.getElementById('id_code');
            const name = document.getElementById('id_name');
            const credit = document.getElementById('id_credit');
            const teacher = document.getElementById('id_teacher');
            const department = document.getElementById('id_department');
            const classTime = document.getElementById('id_class_time');
            const location = document.getElementById('id_location');
            const capacity = document.getElementById('id_capacity');
            const semester = document.getElementById('id_semester');
            const status = document.getElementById('id_status');
            
            // 清除之前的错误提示
            clearErrors();
            
            // 验证课程编号
            if (!code.value.trim()) {
                showError(code, '请输入课程编号');
                isValid = false;
            } else if (code.value.length > 20) {
                showError(code, '课程编号不能超过20个字符');
                isValid = false;
            }
            
            // 验证课程名称
            if (!name.value.trim()) {
                showError(name, '请输入课程名称');
                isValid = false;
            } else if (name.value.length > 100) {
                showError(name, '课程名称不能超过100个字符');
                isValid = false;
            }
            
            // 验证学分
            if (!credit.value) {
                showError(credit, '请输入学分');
                isValid = false;
            } else if (isNaN(credit.value) || parseFloat(credit.value) <= 0 || parseFloat(credit.value) > 10) {
                showError(credit, '学分必须是0.5到10之间的数字');
                isValid = false;
            }
            
            // 验证教师
            if (!teacher.value.trim()) {
                showError(teacher, '请输入任课教师');
                isValid = false;
            }
            
            // 验证院系
            if (!department.value) {
                showError(department, '请选择所属院系');
                isValid = false;
            }
            
            // 验证上课时间
            if (!classTime.value.trim()) {
                showError(classTime, '请输入上课时间');
                isValid = false;
            }
            
            // 验证上课地点
            if (!location.value.trim()) {
                showError(location, '请输入上课地点');
                isValid = false;
            }
            
            // 验证课程容量
            if (!capacity.value) {
                showError(capacity, '请输入课程容量');
                isValid = false;
            } else if (isNaN(capacity.value) || parseInt(capacity.value) <= 0) {
                showError(capacity, '课程容量必须是正整数');
                isValid = false;
            }
            
            // 验证开课学期
            if (!semester.value.trim()) {
                showError(semester, '请输入开课学期');
                isValid = false;
            }
            
            // 验证课程状态
            if (!status.value) {
                showError(status, '请选择课程状态');
                isValid = false;
            }
            
            // 如果表单无效，阻止提交
            if (!isValid) {
                event.preventDefault();
            }
        });
    }
    
    /**
     * 显示错误提示
     * @param {HTMLElement} element - 输入元素
     * @param {string} message - 错误消息
     */
    function showError(element, message) {
        // 添加错误样式
        element.classList.add('is-invalid');
        
        // 创建错误提示元素
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        // 将错误提示添加到输入元素后面
        element.parentNode.appendChild(errorDiv);
    }
    
    /**
     * 清除所有错误提示
     */
    function clearErrors() {
        // 移除所有错误样式
        const invalidInputs = document.querySelectorAll('.is-invalid');
        invalidInputs.forEach(input => {
            input.classList.remove('is-invalid');
        });
        
        // 移除所有错误提示
        const errorMessages = document.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(msg => {
            msg.remove();
        });
    }
}); 