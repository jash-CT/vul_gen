package repositories

import (
	"user_management/internal/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func NewPostgresConnection(dsn string) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	// Auto-migrate models
	err = db.AutoMigrate(
		&models.User{},
		&models.Tenant{},
		&models.Role{},
		&models.Permission{},
	)
	if err != nil {
		return nil, err
	}

	return db, nil
}