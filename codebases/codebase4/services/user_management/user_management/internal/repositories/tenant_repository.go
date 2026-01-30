package repositories

import (
	"user_management/internal/models"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type TenantRepository struct {
	db *gorm.DB
}

func NewTenantRepository(db *gorm.DB) *TenantRepository {
	return &TenantRepository{db: db}
}

func (r *TenantRepository) CreateTenant(tenant *models.Tenant) error {
	return r.db.Create(tenant).Error
}

func (r *TenantRepository) FindTenantByDomain(domain string) (*models.Tenant, error) {
	var tenant models.Tenant
	result := r.db.Where("domain = ?", domain).First(&tenant)
	if result.Error != nil {
		return nil, result.Error
	}
	return &tenant, nil
}

func (r *TenantRepository) UpdateTenantStatus(tenantID uuid.UUID, status models.TenantStatus) error {
	return r.db.Model(&models.Tenant{}).Where("id = ?", tenantID).Update("status", status).Error
}